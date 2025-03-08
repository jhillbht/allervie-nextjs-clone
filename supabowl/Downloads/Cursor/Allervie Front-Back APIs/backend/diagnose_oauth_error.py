#!/usr/bin/env python
"""
OAuth and Google Ads API Diagnostic Tool

This script performs a comprehensive diagnosis of OAuth tokens and Google Ads API configuration
to identify the exact cause of authentication failures.
"""

import os
import sys
import json
import yaml
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oauth_diagnosis')

def get_yaml_path():
    """Get the path to the google-ads.yaml file."""
    base_dir = Path(__file__).parent.parent
    credentials_dir = base_dir / "credentials"
    return credentials_dir / "google-ads.yaml"

def load_yaml_config():
    """Load and validate the Google Ads YAML configuration."""
    yaml_path = get_yaml_path()
    print(f"\n=== Loading YAML configuration from {yaml_path} ===")
    
    try:
        with open(yaml_path, 'r') as f:
            content = f.read()
        
        config = yaml.safe_load(content)
        return config
    except Exception as e:
        print(f"Error loading YAML: {type(e).__name__}: {e}")
        return None

def validate_refresh_token(refresh_token):
    """Check if the refresh token looks valid in format."""
    print("\n=== Validating refresh token format ===")
    
    if not refresh_token:
        print("❌ Refresh token is empty or None")
        return False
        
    # Check token length (typical Google refresh tokens are long)
    if len(refresh_token) < 20:
        print(f"❌ Refresh token is too short: {len(refresh_token)} chars")
        return False
    
    # Check if token starts with typical Google OAuth prefix
    if not refresh_token.startswith("1//"):
        print(f"⚠️ Warning: Refresh token doesn't start with the expected '1//' prefix: {refresh_token[:5]}...")
    
    print(f"✓ Refresh token format looks reasonable (length: {len(refresh_token)} chars)")
    return True

def test_token_refresh(config):
    """
    Test token refresh directly with Google OAuth server.
    This bypasses the Google Ads client to isolate OAuth issues.
    """
    print("\n=== Testing direct token refresh with Google OAuth ===")
    
    if not config:
        print("❌ No configuration available")
        return False
    
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    refresh_token = config.get('refresh_token')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Missing required OAuth credentials")
        return False
    
    # Prepare the token refresh request
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    try:
        print(f"Attempting to refresh token directly with Google OAuth server...")
        response = requests.post(token_url, data=data)
        
        # Log the full response for debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        
        try:
            response_data = response.json()
            print(f"Response body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response body (not JSON): {response.text[:200]}")
        
        if response.status_code == 200:
            print("✓ Successfully refreshed token!")
            
            # Extract useful info from the response
            if 'expires_in' in response_data:
                expires_in = response_data['expires_in']
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                print(f"Token expires in {expires_in} seconds (at {expires_at})")
            
            return True
        else:
            print(f"❌ Failed to refresh token: HTTP {response.status_code}")
            
            # Extract error details
            if response_data.get('error'):
                error = response_data.get('error')
                error_desc = response_data.get('error_description', 'No description')
                
                print(f"Error code: {error}")
                print(f"Error description: {error_desc}")
                
                # Provide specific guidance based on error code
                if error == 'invalid_grant':
                    print("\nThis error typically means:")
                    print("1. The refresh token has expired or been revoked")
                    print("2. The account has changed its password")
                    print("3. The refresh token was generated for a different client ID")
                    print("\nSolution: Generate a new refresh token")
                elif error == 'invalid_client':
                    print("\nThis error means the client_id or client_secret is invalid")
                    print("Solution: Check your OAuth client credentials in Google Cloud Console")
            
            return False
    except Exception as e:
        print(f"❌ Exception during token refresh: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_auth_refresh(config):
    """
    Test token refresh using the Google Auth library.
    This is how the Google Ads client will refresh the token.
    """
    print("\n=== Testing token refresh with Google Auth library ===")
    
    if not config:
        print("❌ No configuration available")
        return False
    
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    refresh_token = config.get('refresh_token')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Missing required OAuth credentials")
        return False
    
    try:
        print("Creating Credentials object...")
        token_uri = "https://oauth2.googleapis.com/token"
        creds = Credentials(
            None,  # No access token
            refresh_token=refresh_token,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret
        )
        
        print("Refreshing token...")
        creds.refresh(Request())
        
        print("✓ Successfully refreshed token!")
        print(f"New access token: {creds.token[:10]}...{creds.token[-10:] if creds.token else ''}")
        print(f"Token expiry: {creds.expiry}")
        
        return True
    except RefreshError as e:
        print(f"❌ RefreshError: {e}")
        print("\nThis typically means:")
        print("1. The refresh token has expired or been revoked")
        print("2. The account has changed its password")
        print("3. The refresh token was generated for a different client ID")
        print("\nSolution: Generate a new refresh token")
        return False
    except Exception as e:
        print(f"❌ Exception during Google Auth refresh: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_google_cloud_project(config):
    """Check if the Google Cloud project has the necessary APIs enabled."""
    print("\n=== Checking Google Cloud project configuration ===")
    
    if not config:
        print("❌ No configuration available")
        return
    
    client_id = config.get('client_id', '')
    
    # Extract project ID from client ID (if possible)
    project_id = None
    if client_id and '.apps.googleusercontent.com' in client_id:
        parts = client_id.split('-')
        if len(parts) > 1:
            project_id = parts[0]
    
    if project_id:
        print(f"Detected project ID: {project_id}")
        print("\nMake sure the following APIs are enabled in this project:")
    else:
        print("Could not determine project ID from client_id")
        print("\nMake sure the following APIs are enabled in your Google Cloud project:")
    
    print("1. Google Ads API")
    print("2. Google Analytics API")
    print("3. Google OAuth2 API")
    
    print("\nCheck in Google Cloud Console: https://console.cloud.google.com/apis/dashboard")

def suggest_solutions():
    """Provide detailed solutions based on the test results."""
    print("\n=== Suggested Solutions ===")
    print("\n1. Generate a new refresh token:")
    print("   python backend/get_refresh_token.py")
    print("\n2. Verify your Google Cloud project settings:")
    print("   - Make sure the OAuth consent screen is configured correctly")
    print("   - Ensure all necessary APIs are enabled")
    print("   - Check that the OAuth client ID has the right redirect URIs")
    print("\n3. Check your Google Ads API settings:")
    print("   - Verify your developer token is valid")
    print("   - Make sure your Google Ads account has API access enabled")
    print("   - Confirm you have the necessary permissions for the account")

def main():
    """Main diagnostic function."""
    print("\n===========================================")
    print("  OAuth and Google Ads API Diagnostic Tool  ")
    print("===========================================\n")
    
    # Load and validate YAML config
    config = load_yaml_config()
    if not config:
        print("❌ Failed to load YAML configuration. Cannot proceed.")
        return 1
    
    # Check for required fields
    missing_fields = []
    for field in ['developer_token', 'client_id', 'client_secret', 'refresh_token', 'login_customer_id']:
        if field not in config or not config[field]:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields in YAML: {', '.join(missing_fields)}")
        if 'refresh_token' in missing_fields:
            print("You need to generate a refresh token. Run: python backend/get_refresh_token.py")
        return 1
    
    # Validate refresh token format
    if 'refresh_token' in config:
        validate_refresh_token(config['refresh_token'])
    
    # Test token refresh directly with OAuth server
    oauth_success = test_token_refresh(config)
    
    # Test token refresh with Google Auth library
    if not oauth_success:
        auth_success = test_google_auth_refresh(config)
    else:
        auth_success = True
        print("\n✓ Google Auth library test skipped (direct OAuth test was successful)")
    
    # Check Google Cloud project configuration
    check_google_cloud_project(config)
    
    # Provide summary and solutions
    print("\n=== Diagnosis Summary ===")
    if oauth_success and auth_success:
        print("✅ OAuth token refresh is working properly")
        print("If you're still having issues with the Google Ads API, it might be related to:")
        print("- Developer token permissions")
        print("- Google Ads account access")
        print("- Incorrect customer ID format")
    else:
        print("❌ OAuth token refresh is failing")
        suggest_solutions()
    
    return 0 if oauth_success and auth_success else 1

if __name__ == "__main__":
    sys.exit(main())
