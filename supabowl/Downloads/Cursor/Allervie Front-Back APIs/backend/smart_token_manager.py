#!/usr/bin/env python
"""
Google Ads API - Smart Refresh Token Manager

This module intelligently manages Google Ads API refresh tokens by:
1. Only replacing tokens when they're actually invalid
2. Maintaining token validity without unnecessary refreshes
3. Minimizing user authentication prompts

Usage:
- Run as standalone script: python smart_token_manager.py
- Import and use in your application: 
  from smart_token_manager import verify_ads_token
  verify_ads_token(force_refresh=False)
"""

import os
import json
import time
import logging
import pathlib
import webbrowser
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import threading
import requests
import yaml
from dotenv import load_dotenv
import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('smart_token_manager')

# Load environment variables
load_dotenv()

# OAuth configuration
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/analytics',
    'https://www.googleapis.com/auth/analytics.edit'
]

# Global variables for the OAuth callback server
authorization_code = None
server_closed = threading.Event()

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for OAuth callback."""
    
    def do_GET(self):
        """Handle GET request with OAuth callback."""
        global authorization_code
        
        # Parse the query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <head><title>Authentication Successful</title></head>
            <body>
                <h1>Authentication Successful!</h1>
                <p>You have successfully authenticated with Google. You may close this window.</p>
                <script>window.close();</script>
            </body>
            </html>
            """
            
            self.wfile.write(response.encode('utf-8'))
            server_closed.set()  # Signal that we can stop the server
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <head><title>Authentication Failed</title></head>
            <body>
                <h1>Authentication Failed</h1>
                <p>No authorization code was received from Google. Please try again.</p>
            </body>
            </html>
            """
            
            self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress the default logging."""
        return

def get_file_paths():
    """Get paths to necessary files."""
    base_dir = pathlib.Path(__file__).parent.parent
    credentials_dir = base_dir / 'credentials'
    
    # Create credentials directory if it doesn't exist
    credentials_dir.mkdir(exist_ok=True)
    
    yaml_path = credentials_dir / 'google-ads.yaml'
    client_secret_path = credentials_dir / 'client_secret.json'
    token_status_path = credentials_dir / '.token_status.json'
    
    return {
        'base_dir': base_dir,
        'credentials_dir': credentials_dir,
        'yaml_path': yaml_path,
        'client_secret_path': client_secret_path,
        'token_status_path': token_status_path
    }

def load_client_config():
    """Load the OAuth client configuration."""
    paths = get_file_paths()
    
    if not paths['client_secret_path'].exists():
        logger.error(f"Client secrets file not found at {paths['client_secret_path']}")
        return None
    
    try:
        with open(paths['client_secret_path'], 'r') as f:
            client_secrets = json.load(f)
        
        # Extract client configuration
        if 'web' in client_secrets:
            client_config = client_secrets['web']
        elif 'installed' in client_secrets:
            client_config = client_secrets['installed']
        else:
            logger.error("Invalid client secrets file format")
            return None
        
        # Get required values
        client_id = client_config.get('client_id')
        client_secret = client_config.get('client_secret')
        
        if not client_id or not client_secret:
            logger.error("Client ID or Client Secret not found in the client secrets file")
            return None
        
        # Use redirect URI from client secrets if available, otherwise use default
        redirect_uris = client_config.get('redirect_uris', [])
        redirect_uri = redirect_uris[0] if redirect_uris else 'http://localhost:8080'
        
        return {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
    
    except Exception as e:
        logger.error(f"Error loading client secrets file: {e}")
        return None

def load_yaml_config():
    """Load the Google Ads API YAML configuration."""
    paths = get_file_paths()
    
    if not paths['yaml_path'].exists():
        logger.warning(f"Google Ads YAML file not found at {paths['yaml_path']}")
        return None
    
    try:
        with open(paths['yaml_path'], 'r') as f:
            config = yaml.safe_load(f) or {}
        
        return config
    
    except Exception as e:
        logger.error(f"Error loading YAML configuration: {e}")
        return None

def update_yaml_config(config):
    """Update the Google Ads API YAML configuration."""
    paths = get_file_paths()
    
    try:
        with open(paths['yaml_path'], 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Updated Google Ads YAML configuration at {paths['yaml_path']}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating YAML configuration: {e}")
        return False

def load_token_status():
    """Load token status information from the status file."""
    paths = get_file_paths()
    
    if not paths['token_status_path'].exists():
        # If file doesn't exist, return default status
        return {
            'last_check': None,
            'last_refresh': None,
            'validity_checks': 0,
            'failed_checks': 0
        }
    
    try:
        with open(paths['token_status_path'], 'r') as f:
            status = json.load(f)
        
        # Convert string dates back to datetime objects
        if status.get('last_check'):
            status['last_check'] = datetime.datetime.fromisoformat(status['last_check'])
        if status.get('last_refresh'):
            status['last_refresh'] = datetime.datetime.fromisoformat(status['last_refresh'])
        
        return status
    
    except Exception as e:
        logger.error(f"Error loading token status: {e}")
        return {
            'last_check': None,
            'last_refresh': None,
            'validity_checks': 0,
            'failed_checks': 0
        }

def update_token_status(status):
    """Update the token status file."""
    paths = get_file_paths()
    
    # Convert datetime objects to strings for JSON serialization
    status_copy = status.copy()
    if status_copy.get('last_check'):
        status_copy['last_check'] = status_copy['last_check'].isoformat()
    if status_copy.get('last_refresh'):
        status_copy['last_refresh'] = status_copy['last_refresh'].isoformat()
    
    try:
        with open(paths['token_status_path'], 'w') as f:
            json.dump(status_copy, f, indent=2)
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating token status: {e}")
        return False

def test_google_ads_api_access(yaml_config):
    """
    Test if the Google Ads API is accessible with the current configuration.
    This is the most reliable way to verify if the refresh token is valid.
    
    Returns:
        bool: True if access is successful, False otherwise
    """
    try:
        # Create client from dictionary
        temp_yaml_path = get_file_paths()['credentials_dir'] / 'temp_google-ads.yaml'
        with open(temp_yaml_path, 'w') as f:
            yaml.dump(yaml_config, f, default_flow_style=False)
        
        client = GoogleAdsClient.load_from_storage(str(temp_yaml_path))
        
        # Test a simple API call
        ga_service = client.get_service("GoogleAdsService")
        customer_id = client.login_customer_id
        
        # Create a simple query to test access
        query = """
            SELECT
              customer.id,
              customer.descriptive_name
            FROM customer
            LIMIT 1
        """
        
        # Execute the query
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        # If this executes without error, the token is valid
        response = ga_service.search(request=search_request)
        
        # Clean up temporary file
        os.remove(temp_yaml_path)
        
        return True
    
    except GoogleAdsException as ex:
        # Don't consider permission errors as token invalidity
        if ex.error.code().name == "AUTHENTICATION_ERROR":
            logger.error(f"Authentication error: {ex}")
            return False
        elif ex.error.code().name == "CUSTOMER_NOT_FOUND":
            # This means the token works but customer ID is wrong
            logger.warning(f"Customer ID error: {ex}")
            return True
        else:
            # Other API errors don't mean the token is invalid
            logger.warning(f"API error but token might be valid: {ex}")
            return True
    
    except Exception as e:
        logger.error(f"Error testing Google Ads API access: {e}")
        return False

def should_refresh_token(force_refresh=False):
    """
    Determine if the refresh token should be refreshed based on status and configuration.
    
    Args:
        force_refresh (bool): If True, force token refresh regardless of status
        
    Returns:
        bool: True if the token should be refreshed, False otherwise
    """
    if force_refresh:
        logger.info("Force refresh requested, will refresh token")
        return True
    
    # Load current configuration and status
    yaml_config = load_yaml_config()
    token_status = load_token_status()
    
    # If no configuration exists or no refresh token, we need a new one
    if not yaml_config or 'refresh_token' not in yaml_config or not yaml_config['refresh_token']:
        logger.info("No refresh token found, will generate a new one")
        return True
    
    # Check if we've recently verified the token's validity
    now = datetime.datetime.now()
    if token_status['last_check']:
        hours_since_check = (now - token_status['last_check']).total_seconds() / 3600
        
        # If we've checked recently and it was valid, don't check again
        if hours_since_check < 1 and token_status['failed_checks'] == 0:
            logger.info(f"Token was checked {hours_since_check:.2f} hours ago and was valid")
            return False
    
    # Test if the current token is valid
    logger.info("Testing current refresh token validity...")
    token_status['last_check'] = now
    token_status['validity_checks'] += 1
    
    if test_google_ads_api_access(yaml_config):
        logger.info("Refresh token is valid, no need to refresh")
        token_status['failed_checks'] = 0
        update_token_status(token_status)
        return False
    
    # Token is not valid, increment failed checks
    logger.warning("Refresh token is invalid or expired")
    token_status['failed_checks'] += 1
    update_token_status(token_status)
    
    return True

def start_oauth_callback_server(port=8080):
    """Start a local server to receive the OAuth callback."""
    global server_closed
    server_closed.clear()
    
    # Try to create a TCP server with retries on port conflicts
    max_retries = 5
    retry_count = 0
    httpd = None
    
    while retry_count < max_retries:
        try:
            httpd = socketserver.TCPServer(("localhost", port), OAuthCallbackHandler)
            break
        except OSError as e:
            if "Address already in use" in str(e):
                retry_count += 1
                logger.warning(f"Port {port} is in use, trying port {port + retry_count}")
                port += 1
            else:
                raise
    
    if not httpd:
        logger.error("Failed to start OAuth callback server after retries")
        return None
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    logger.info(f"Started OAuth callback server on port {port}")
    
    # Wait for the callback
    server_closed.wait(timeout=300)  # 5 minutes timeout
    
    # Shutdown the server
    httpd.shutdown()
    httpd.server_close()
    logger.info("OAuth callback server stopped")
    
    return port

def get_authorization_url(client_id, redirect_uri):
    """Generate the OAuth authorization URL."""
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'  # Force consent screen to always get a refresh token
    }
    
    # Build the query string
    query_string = '&'.join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
    
    return f"https://accounts.google.com/o/oauth2/auth?{query_string}"

def exchange_code_for_tokens(code, client_id, client_secret, redirect_uri):
    """Exchange an authorization code for access and refresh tokens."""
    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info("Successfully exchanged code for tokens")
            return token_data
        else:
            logger.error(f"Token exchange failed: {response.json().get('error')}")
            return None
    
    except Exception as e:
        logger.error(f"Error exchanging code for tokens: {e}")
        return None

def generate_new_refresh_token():
    """Generate a new refresh token using the OAuth flow."""
    global authorization_code
    authorization_code = None
    
    # Load client configuration
    client_config = load_client_config()
    if not client_config:
        logger.error("Failed to load client configuration")
        return None
    
    client_id = client_config['client_id']
    client_secret = client_config['client_secret']
    redirect_uri = client_config['redirect_uri']
    
    # Adjust redirect URI to use a consistent port
    if 'localhost' in redirect_uri:
        redirect_uri = 'http://localhost:8080'
    
    # Start the callback server
    callback_port = start_oauth_callback_server(8080)
    if callback_port is None:
        return None
    
    # Update redirect URI with the actual port used
    redirect_uri = f"http://localhost:{callback_port}"
    
    # Generate and open the authorization URL
    auth_url = get_authorization_url(client_id, redirect_uri)
    logger.info(f"Opening authorization URL: {auth_url}")
    
    # Try to open the browser
    browser_opened = webbrowser.open(auth_url)
    
    if not browser_opened:
        logger.warning("Could not open the browser automatically.")
        logger.info(f"Please open this URL manually to complete authorization: {auth_url}")
    
    # Wait for the callback to complete (with timeout)
    max_wait = 300  # 5 minutes
    wait_interval = 2  # seconds
    waited = 0
    
    logger.info("Waiting for authorization...")
    
    while authorization_code is None and waited < max_wait:
        time.sleep(wait_interval)
        waited += wait_interval
    
    # Check if we got the code
    if authorization_code is None:
        logger.error("Timed out waiting for authorization code")
        return None
    
    logger.info("Authorization code received, exchanging for tokens...")
    
    # Exchange the code for tokens
    token_data = exchange_code_for_tokens(authorization_code, client_id, client_secret, redirect_uri)
    
    if token_data and 'refresh_token' in token_data:
        logger.info("Successfully generated new refresh token")
        return token_data['refresh_token']
    else:
        logger.error("Failed to get refresh token from token response")
        return None

def verify_ads_token(force_refresh=False):
    """
    Verify and refresh the Google Ads API token if necessary.
    
    This function:
    1. Checks if the current refresh token is valid
    2. Only generates a new one if necessary
    3. Updates the YAML configuration file
    
    Args:
        force_refresh (bool): If True, force token refresh regardless of status
    
    Returns:
        bool: True if a valid refresh token is available, False otherwise
    """
    # Check if we need to refresh the token
    if not should_refresh_token(force_refresh):
        logger.info("Token is valid, no refresh needed")
        return True
    
    # Load client configuration
    client_config = load_client_config()
    if not client_config:
        logger.error("Failed to load client configuration")
        return False
    
    # Generate a new refresh token
    logger.info("Generating new refresh token...")
    new_refresh_token = generate_new_refresh_token()
    
    if not new_refresh_token:
        logger.error("Failed to generate a new refresh token")
        return False
    
    # Load and update the YAML configuration
    yaml_config = load_yaml_config() or {}
    
    yaml_config['client_id'] = client_config['client_id']
    yaml_config['client_secret'] = client_config['client_secret']
    yaml_config['refresh_token'] = new_refresh_token
    
    # Add other required fields if missing
    if 'developer_token' not in yaml_config:
        yaml_config['developer_token'] = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    
    if 'login_customer_id' not in yaml_config:
        yaml_config['login_customer_id'] = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
    
    if 'use_proto_plus' not in yaml_config:
        yaml_config['use_proto_plus'] = True
    
    # Write the updated configuration
    success = update_yaml_config(yaml_config)
    
    if success:
        # Update token status
        token_status = load_token_status()
        token_status['last_refresh'] = datetime.datetime.now()
        token_status['last_check'] = datetime.datetime.now()
        token_status['failed_checks'] = 0
        update_token_status(token_status)
        
        logger.info("Successfully updated configuration with new refresh token")
        return True
    else:
        logger.error("Failed to update configuration")
        return False

def main():
    """Main function to run as a standalone script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Google Ads API Token Manager')
    parser.add_argument('--force', action='store_true', help='Force refresh of the token')
    args = parser.parse_args()
    
    # Verify and refresh the token if needed
    if verify_ads_token(force_refresh=args.force):
        logger.info("Token verification completed successfully")
        
        # Test the connection
        yaml_config = load_yaml_config()
        if test_google_ads_api_access(yaml_config):
            logger.info("✅ Google Ads API connection is working properly")
        else:
            logger.error("❌ Google Ads API connection test failed")
    else:
        logger.error("❌ Token verification failed")

if __name__ == "__main__":
    main()
