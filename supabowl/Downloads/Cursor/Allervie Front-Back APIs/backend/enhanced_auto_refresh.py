#!/usr/bin/env python
"""
Enhanced Google Ads API Token Auto-Refresh Module

This module provides automatic refresh of Google OAuth tokens for Google Ads API
with improved error handling, token validation, and support for environment variables.
It is designed to be called either directly or as part of the main application.
"""

import os
import json
import logging
import datetime
import pathlib
from pathlib import Path
import yaml
import traceback
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Ads API OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/analytics',
    'https://www.googleapis.com/auth/analytics.edit'
]

def find_token_file():
    """Find the token.json file in various possible locations."""
    possible_paths = [
        Path(__file__).parent / "token.json",
        Path(__file__).parent.parent / "credentials" / "token.json",
        Path.cwd() / "token.json",
        Path.cwd() / "credentials" / "token.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found token.json at: {path}")
            return path
    
    logger.warning("token.json not found")
    return None

def find_client_secrets():
    """Find the client_secret.json file in various possible locations."""
    possible_paths = [
        Path(__file__).parent / "client_secret.json",
        Path(__file__).parent.parent / "credentials" / "client_secret.json",
        Path.cwd() / "client_secret.json",
        Path.cwd() / "credentials" / "client_secret.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found client_secret.json at: {path}")
            return path
    
    logger.warning("client_secret.json not found")
    return None

def find_yaml_file():
    """Find the google-ads.yaml file in various possible locations."""
    possible_paths = [
        Path(__file__).parent / "google-ads.yaml",
        Path(__file__).parent.parent / "credentials" / "google-ads.yaml",
        Path.cwd() / "google-ads.yaml",
        Path.cwd() / "credentials" / "google-ads.yaml",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found google-ads.yaml at: {path}")
            return path
    
    logger.warning("google-ads.yaml not found")
    return None

def is_token_expired(token_data):
    """Check if the token is expired or about to expire."""
    # Check if the token has an expiry field
    if 'expiry' not in token_data:
        logger.warning("Token does not have expiry data, assuming expired")
        return True
    
    try:
        # Parse the expiry date
        expiry = datetime.datetime.fromisoformat(token_data['expiry'])
        
        # Add a buffer (refresh if less than 10 minutes of validity left)
        buffer_time = datetime.timedelta(minutes=10)
        
        # Check if expired or will expire soon
        is_expired = expiry - buffer_time <= datetime.datetime.now()
        
        if is_expired:
            logger.info(f"Token is expired or will expire soon (expiry: {expiry})")
        else:
            logger.info(f"Token is still valid until {expiry}")
        
        return is_expired
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing token expiry: {e}")
        # If we can't parse the expiry, assume it's expired to be safe
        return True

def update_yaml_with_token(yaml_path, refresh_token):
    """Update the google-ads.yaml file with the new refresh token."""
    try:
        # Load the existing yaml file
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update the refresh token
        config['refresh_token'] = refresh_token
        
        # Save the updated yaml file
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Successfully updated {yaml_path} with the new refresh token")
        return True
    except Exception as e:
        logger.error(f"Error updating google-ads.yaml: {e}")
        logger.error(traceback.format_exc())
        return False

def update_env_variables(refresh_token):
    """Update environment variables with the new refresh token."""
    os.environ['GOOGLE_ADS_REFRESH_TOKEN'] = refresh_token
    logger.info("Updated GOOGLE_ADS_REFRESH_TOKEN environment variable")
    return True

def refresh_token_if_needed(force=False):
    """
    Check if the token needs to be refreshed and refresh it if necessary.
    
    Args:
        force (bool): Force token refresh even if not expired
        
    Returns:
        bool: True if refresh successful or not needed, False on failure
    """
    try:
        # Find token file
        token_path = find_token_file()
        
        # Load token data
        if token_path and token_path.exists():
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            # Check if token is expired or force refresh
            if not force and not is_token_expired(token_data):
                logger.info("Token is still valid, no refresh needed")
                return True
            
            # Prepare credentials for refresh
            try:
                credentials = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes', SCOPES)
                )
                
                # Refresh the token
                if credentials.expired or force:
                    logger.info("Refreshing token...")
                    credentials.refresh(Request())
                    
                    # Save the refreshed credentials
                    token_json = {
                        'token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'token_uri': credentials.token_uri,
                        'client_id': credentials.client_id,
                        'client_secret': credentials.client_secret,
                        'scopes': credentials.scopes,
                        'expiry': credentials.expiry.isoformat()
                    }
                    
                    with open(token_path, 'w') as token_file:
                        json.dump(token_json, token_file)
                    
                    logger.info(f"Token refreshed and saved to {token_path}")
                    
                    # Update yaml file if it exists
                    yaml_path = find_yaml_file()
                    if yaml_path:
                        update_yaml_with_token(yaml_path, credentials.refresh_token)
                    
                    # Update environment variables
                    update_env_variables(credentials.refresh_token)
                    
                    return True
                else:
                    logger.info("Token is already valid, no refresh needed")
                    return True
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                logger.error(traceback.format_exc())
                
                # If refresh fails, we need to generate a new token through full authorization
                return generate_new_token()
        else:
            logger.warning("Token file not found, need to generate new token")
            return generate_new_token()
    except Exception as e:
        logger.error(f"Error in refresh_token_if_needed: {e}")
        logger.error(traceback.format_exc())
        return False

def generate_new_token(port=8080):
    """
    Generate a new token through full OAuth flow.
    
    Args:
        port (int): Port to use for OAuth callback server
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Find client secrets file
        client_secrets_path = find_client_secrets()
        if not client_secrets_path:
            logger.error("Client secrets file not found, cannot generate new token")
            return False
        
        # Determine paths for saving tokens
        token_path = find_token_file()
        if not token_path:
            # Create token.json in the same directory as this script
            token_path = Path(__file__).parent / "token.json"
        
        # Create the flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_path,
            scopes=SCOPES,
            redirect_uri=f"http://localhost:{port}"
        )
        
        # Run the authorization flow (this will open a browser)
        logger.info("Running OAuth flow to generate new token...")
        credentials = flow.run_local_server(port=port)
        
        # Save the credentials
        token_json = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        # Ensure directory exists
        token_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save token
        with open(token_path, 'w') as token_file:
            json.dump(token_json, token_file)
        
        logger.info(f"New token generated and saved to {token_path}")
        
        # Update yaml file if it exists
        yaml_path = find_yaml_file()
        if yaml_path:
            update_yaml_with_token(yaml_path, credentials.refresh_token)
        
        # Update environment variables
        update_env_variables(credentials.refresh_token)
        
        return True
    except Exception as e:
        logger.error(f"Error generating new token: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """
    Main function to run as a standalone script.
    """
    print("\n===== Enhanced Google Ads API Token Auto-Refresh =====\n")
    
    # Check if force refresh is needed
    force_refresh = input("Force token refresh? (y/N): ").lower() == 'y'
    
    # Refresh token
    if refresh_token_if_needed(force=force_refresh):
        print("\n✅ Token refresh successful!\n")
        
        # Print token file details
        token_path = find_token_file()
        if token_path:
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            # Print some details (but hide sensitive parts)
            if 'token' in token_data:
                token = token_data['token']
                print(f"Access Token: {token[:10]}...{token[-5:]}")
            
            if 'refresh_token' in token_data:
                refresh_token = token_data['refresh_token']
                print(f"Refresh Token: {refresh_token[:10]}...{refresh_token[-5:]}")
            
            if 'expiry' in token_data:
                print(f"Expiry: {token_data['expiry']}")
            
            if 'scopes' in token_data:
                print(f"Scopes: {len(token_data['scopes'])} scope(s) defined")
        
        print("\nToken has been refreshed successfully. You can now use the Google Ads API.")
        return 0
    else:
        print("\n❌ Token refresh failed.\n")
        print("Please check the logs for more details.")
        print("You may need to get a new refresh token through the OAuth flow.")
        print("Try running 'python oauth_server.py'")
        return 1

if __name__ == "__main__":
    exit(main())