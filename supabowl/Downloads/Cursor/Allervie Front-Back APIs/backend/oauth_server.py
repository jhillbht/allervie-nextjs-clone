#!/usr/bin/env python
"""
Google OAuth Server for Allervie Dashboard

This script creates a standalone OAuth server to get a valid refresh token
for Google APIs including Google Ads API.
"""

import os
import json
import webbrowser
import http.server
import socketserver
import threading
import urllib.parse
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
PORT = 49153  # Match one of the redirect_uris in client_secret.json
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/analytics',
    'https://www.googleapis.com/auth/analytics.edit'
]

# Global variables
authorization_code = None
server_closed = threading.Event()

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for OAuth callback."""
    
    def do_GET(self):
        """Handle GET request with OAuth callback."""
        global authorization_code
        
        # Parse the query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if 'code' in query_components:
            authorization_code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <head><title>Authentication Successful</title></head>
            <body>
                <h1>Authentication Successful!</h1>
                <p>You have successfully authenticated with Google. You can close this window and return to the terminal.</p>
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
        """Customize logging."""
        logger.info(f"OAuth Server: {args[0]} {args[1]} {args[2]}")

def get_client_secret_path():
    """Find the client_secret.json file."""
    # Try different locations
    possible_paths = [
        Path(__file__).parent / "client_secret.json",
        Path(__file__).parent.parent / "credentials" / "client_secret.json",
        Path.cwd() / "client_secret.json",
        Path.cwd() / "credentials" / "client_secret.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found client_secret.json at: {path}")
            return str(path)
    
    logger.error("client_secret.json not found")
    return None

def get_refresh_token():
    """Main function to get a refresh token."""
    client_secret_path = get_client_secret_path()
    if not client_secret_path:
        return False
    
    redirect_uri = f"http://localhost:{PORT}"
    token_path = Path(__file__).parent.parent / "credentials" / "token.json"
    
    # Start the callback server in a separate thread
    server_closed.clear()
    httpd = socketserver.TCPServer(("localhost", PORT), OAuthCallbackHandler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    logger.info(f"Started OAuth callback server on port {PORT}")
    
    try:
        # Load client secrets
        with open(client_secret_path, 'r') as f:
            client_config = json.load(f)
        
        # Create the flow
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to always get a refresh token
        )
        
        # Open the browser for the user
        print("\nPlease open the following URL in your browser:")
        print(auth_url)
        print("\nIf it doesn't open automatically, copy and paste the URL into your browser.\n")
        webbrowser.open(auth_url)
        
        # Wait for the callback
        print("Waiting for authentication...")
        server_closed.wait(timeout=300)  # 5 minutes timeout
        
        if not authorization_code:
            print("No authorization code received.")
            return False
        
        print("\nAuthorization code received. Exchanging for tokens...")
        
        # Exchange code for tokens
        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials
        
        # Save the credentials
        token_json = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as token_file:
            json.dump(token_json, token_file)
        
        # Update the google-ads.yaml file with the new refresh token
        yaml_path = Path(__file__).parent.parent / "credentials" / "google-ads.yaml"
        if yaml_path.exists():
            try:
                import yaml
                with open(yaml_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Update the refresh token
                config['refresh_token'] = credentials.refresh_token
                
                with open(yaml_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                
                print(f"\nSuccessfully updated {yaml_path} with the new refresh token")
            except Exception as e:
                print(f"Error updating google-ads.yaml: {e}")
        
        print("\nAuthentication successful!")
        print(f"Refresh token: {credentials.refresh_token}")
        print(f"Credentials saved to: {token_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in OAuth flow: {e}")
        return False
    finally:
        # Stop the server
        httpd.shutdown()
        httpd.server_close()
        logger.info("OAuth callback server stopped")

if __name__ == "__main__":
    print("=== Google OAuth Token Generator ===")
    success = get_refresh_token()
    if success:
        print("\n✅ OAuth process completed successfully")
    else:
        print("\n❌ OAuth process failed")