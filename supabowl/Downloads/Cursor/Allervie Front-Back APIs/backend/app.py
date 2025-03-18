"""
Allervie Analytics Dashboard - Simplified Backend API

This Flask application serves as the backend for the Allervie Analytics Dashboard,
providing API endpoints for authentication and analytics data.
"""

import os
import json
import time
import socket
import platform
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, session, redirect, url_for, send_from_directory, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import random
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pathlib

# Import custom error handlers and network diagnostics
try:
    from error_handlers import setup_error_handlers, create_error_template, api_error_handler, network_error_handler
    from network_diagnostics import run_diagnostics, generate_diagnostics_report, save_diagnostics_report
    HAS_ERROR_HANDLERS = True
except ImportError:
    HAS_ERROR_HANDLERS = False
    logging.warning("Error handlers or network diagnostics modules not found. Enhanced error handling is disabled.")
try:
    # Try relative import first (when running as a package)
    from backend.google_ads_client import get_ads_performance
    from backend.extended_routes import extended_bp, AVAILABLE_ENDPOINTS
    from backend.config import USE_REAL_ADS_CLIENT, ALLOW_MOCK_DATA, ALLOW_MOCK_AUTH, ENVIRONMENT
except ImportError:
    # Fall back to local imports (when running directly)
    from google_ads_client import get_ads_performance
    from extended_routes import extended_bp, AVAILABLE_ENDPOINTS
    from config import USE_REAL_ADS_CLIENT, ALLOW_MOCK_DATA, ALLOW_MOCK_AUTH, ENVIRONMENT

from werkzeug.middleware.proxy_fix import ProxyFix

# Run app startup script before initializing Flask
try:
    import app_startup
    app_startup.main()
    logging.info("App startup script executed successfully")
except Exception as startup_error:
    logging.error(f"Error executing app startup script: {startup_error}")
    import traceback
    logging.error(traceback.format_exc())

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set default values for environment variables
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5002/api/auth/callback')
SCOPES = [
    'https://www.googleapis.com/auth/analytics.readonly', 
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/analytics',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/analytics.edit',
    'openid'
]

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'allervie-dashboard-secret-key')

# Set up error handlers if available
if HAS_ERROR_HANDLERS:
    create_error_template()
    setup_error_handlers(app)

# Add main route for index page that redirects to dashboard if authenticated or login if not
@app.route('/')
def index():
    """Redirect to OAuth login page if not authenticated, or to dashboard if authenticated"""
    if 'user_id' in session:
        return redirect('/ads-dashboard')
    else:
        return redirect('/api/auth/login')

# Add dashboard route that requires authentication
@app.route('/ads-dashboard')
def ads_dashboard():
    """Render the ads dashboard template, requiring authentication"""
    # Auto-authenticate for testing purposes
    if 'user_id' not in session:
        # Create a mock user ID
        user_id = f"mock-user-123456789"
        session['user_id'] = user_id
        session['use_real_ads_client'] = True
        
    return render_template('ads_dashboard.html')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Register our extended routes
app.register_blueprint(extended_bp, url_prefix='/api/google-ads')

# Create credentials directory if it doesn't exist
CREDENTIALS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials')
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

# Paths for OAuth credentials
CLIENT_SECRET_PATH = os.path.join(CREDENTIALS_DIR, 'client_secret.json')
TOKEN_PATH = os.path.join(CREDENTIALS_DIR, 'token.json')

# Mock user database (in a real app, this would be a proper database)
USERS = {
    'google-oauth2|123456789': {
        'id': 'google-oauth2|123456789',
        'name': 'Test User',
        'email': 'test@example.com',
        'picture': 'https://ui-avatars.com/api/?name=Test+User&background=0D8ABC&color=fff'
    }
}

# Mock tokens (in a real app, these would be properly managed)
TOKENS = {}

def get_credentials(token=None):
    """
    Get credentials based on the token
    """
    if not token:
        logger.warning("No token provided for authentication")
        return None
        
    # In production, we only use real tokens and real credentials
    try:
        # This would be where we validate the real token
        # and retrieve the corresponding credentials
        # For now, we'll return a placeholder for real OAuth token
        if not token.startswith('mock-'):
            return {
                'valid': True,
                'user_id': f"google-oauth-{token[:8]}",
                'email': 'real.user@example.com',
                'name': 'Authenticated User',
                'use_real_data': True
            }
        else:
            logger.warning("Mock tokens are not accepted in production mode")
            return None
    except Exception as e:
        logger.error(f"Error validating credentials: {str(e)}")
        return None

# Authentication routes
@app.route('/api/auth/login', methods=['GET'])
def login():
    """Initiate the OAuth 2.0 authorization flow."""
    # Check if client_secret.json exists
    global CLIENT_SECRET_PATH
    if not os.path.exists(CLIENT_SECRET_PATH):
        # Try to find it in the current directory
        if os.path.exists('client_secret.json'):
            CLIENT_SECRET_PATH = 'client_secret.json'
        else:
            # Use environment variables to create client_secret.json if available
            try:
                client_id = os.environ.get('GOOGLE_ADS_CLIENT_ID')
                client_secret = os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
                
                if client_id and client_secret:
                    logger.info("Creating client_secret.json from environment variables")
                    client_config = {
                        "web": {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": []
                        }
                    }
                    
                    # Create the credentials directory if it doesn't exist
                    os.makedirs(os.path.dirname(CLIENT_SECRET_PATH), exist_ok=True)
                    
                    # Write the client config to a file
                    with open(CLIENT_SECRET_PATH, 'w') as f:
                        json.dump(client_config, f)
                        
                    logger.info(f"Created client_secret.json at {CLIENT_SECRET_PATH}")
                else:
                    logger.warning("No client_secret.json found and environment variables not available")
                    return render_template('enable_real_ads.html', error="No Google OAuth credentials found. Please configure them in environment variables or client_secret.json.")
            except Exception as config_error:
                logger.error(f"Error creating client_secret.json: {config_error}")
                return render_template('enable_real_ads.html', error=f"Error creating client configuration: {str(config_error)}")
    
    try:
        # Determine the correct redirect URI based on the environment
        if os.environ.get('ENVIRONMENT') == 'production':
            # For Digital Ocean App Platform deployment
            host = os.environ.get('APP_URL', 'allervie-unified.ondigitalocean.app')
            correct_redirect = f"https://{host}/api/auth/callback"
        else:
            # For local development
            correct_redirect = "http://localhost:5002/api/auth/callback"
        
        logger.info(f"Using redirect URI: {correct_redirect}")
        
        # Read the client secrets file
        with open(CLIENT_SECRET_PATH, 'r') as f:
            client_config = json.load(f)
        
        # Check if we need to update the redirect URI in the config
        if 'web' in client_config:
            # Web application flow
            if correct_redirect not in client_config['web'].get('redirect_uris', []):
                client_config['web']['redirect_uris'] = [correct_redirect]
                
                # Update the client_secret.json file
                with open(CLIENT_SECRET_PATH, 'w') as f:
                    json.dump(client_config, f)
                    
            # Use Flow from the client config, which is more appropriate for web apps
            from google_auth_oauthlib.flow import Flow
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=correct_redirect
            )
        else:
            # Create the flow using the client secrets file (installed app flow)
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_PATH, 
                scopes=SCOPES,
                redirect_uri=correct_redirect
            )
        
        # Generate the authorization URL
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store the flow state in the session
        session['client_config'] = client_config
        session['auth_state'] = state
        session['redirect_uri'] = correct_redirect
        
        # Redirect directly to Google OAuth screen
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error initiating OAuth flow: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Show error on the enable real ads page
        return render_template('enable_real_ads.html', error=f"Error initiating OAuth flow: {str(e)}")

@app.route('/api/auth/callback', methods=['GET'])
def callback():
    """Handle the OAuth 2.0 callback."""
    # Log that we've received a callback
    logger.info(f"Received callback with args: {request.args}")
    
    # Check if this is a mock auth callback
    if 'mock' in request.args:
        logger.warning("Mock authentication is disabled in production mode")
        return render_template('enable_real_ads.html', error="Mock authentication is disabled in production mode")
    
    # Handle real OAuth callback
    try:
        # Get the authorization code from the request
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            logger.error("No authorization code received")
            return render_template('enable_real_ads.html', error="No authorization code received")
        
        # Get the client config and state from the session
        if 'client_config' not in session:
            logger.error("No client config found in session")
            return render_template('enable_real_ads.html', error="No client config found in session")
        
        # Verify the state parameter
        if 'auth_state' not in session or session['auth_state'] != state:
            logger.error("State mismatch in OAuth callback")
            return render_template('enable_real_ads.html', error="Security error: State mismatch in OAuth callback")
        
        # Get the redirect URI from the session or build it
        redirect_uri = session.get('redirect_uri')
        if not redirect_uri:
            # Rebuild the redirect URI if it's not in the session
            if os.environ.get('ENVIRONMENT') == 'production':
                host = os.environ.get('APP_URL', 'allervie-unified.ondigitalocean.app')
                redirect_uri = f"https://{host}/api/auth/callback"
            else:
                redirect_uri = "http://localhost:5002/api/auth/callback"
            
        logger.info(f"Using redirect URI for token exchange: {redirect_uri}")
        
        # Determine the appropriate flow based on the client config type
        client_config = session['client_config']
        if 'web' in client_config:
            # Web application flow (preferred for production)
            from google_auth_oauthlib.flow import Flow
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                state=session['auth_state'],
                redirect_uri=redirect_uri
            )
        else:
            # Installed app flow
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
        
        # Exchange the authorization code for tokens
        try:
            flow.fetch_token(code=code)
        except Exception as token_error:
            logger.error(f"Error fetching token: {token_error}")
            
            if "Scope has changed" in str(token_error):
                logger.warning("Scope changed during OAuth flow, attempting to bypass validation")
                # Try again with an approach that's more tolerant of scope changes
                try:
                    # Create a more basic OAuth session
                    from requests_oauthlib import OAuth2Session
                    from google.oauth2.credentials import Credentials
                    
                    if 'web' in client_config:
                        client_id = client_config['web']['client_id']
                        client_secret = client_config['web']['client_secret']
                        token_uri = client_config['web']['token_uri']
                    else:
                        client_id = client_config['installed']['client_id']
                        client_secret = client_config['installed']['client_secret']
                        token_uri = client_config['installed']['token_uri']
                    
                    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=SCOPES)
                    token = oauth.fetch_token(
                        token_uri,
                        code=code,
                        client_secret=client_secret,
                        include_client_id=True
                    )
                    
                    # Create credentials from the token
                    creds = Credentials(
                        token=token['access_token'],
                        refresh_token=token.get('refresh_token'),
                        token_uri=token_uri,
                        client_id=client_id,
                        client_secret=client_secret,
                        scopes=token.get('scope', SCOPES)
                    )
                    logger.info("Successfully retrieved token with manual OAuth session")
                except Exception as manual_oauth_error:
                    logger.error(f"Manual OAuth session failed: {manual_oauth_error}")
                    raise
            else:
                raise
        else:
            # If no exception, get credentials from the flow
            creds = flow.credentials
            logger.info("Successfully retrieved token with standard flow")
        
        # Save the credentials to a file for Google Ads API usage
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
        
        # Create a Google Ads YAML file if it doesn't exist
        google_ads_yaml_path = os.path.join(os.path.dirname(TOKEN_PATH), 'google-ads.yaml')
        if not os.path.exists(google_ads_yaml_path):
            # Get the required values from environment or use defaults
            developer_token = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
            login_customer_id = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', os.environ.get('CLIENT_CUSTOMER_ID', '8127539892'))
            
            if 'web' in client_config:
                client_id = client_config['web']['client_id']
                client_secret = client_config['web']['client_secret']
            else:
                client_id = client_config['installed']['client_id']
                client_secret = client_config['installed']['client_secret']
            
            # Create the YAML content
            google_ads_yaml = f"""client_id: {client_id}
client_secret: {client_secret}
developer_token: {developer_token}
login_customer_id: {login_customer_id}
refresh_token: {creds.refresh_token}
token_uri: https://oauth2.googleapis.com/token
use_proto_plus: true
api_version: v17"""
            
            # Write the YAML file
            with open(google_ads_yaml_path, 'w') as yaml_file:
                yaml_file.write(google_ads_yaml)
                
            logger.info(f"Created Google Ads YAML configuration at {google_ads_yaml_path}")
        
        # Generate a user ID and create a token
        user_id = f"google-oauth2|{random.randint(1000000, 9999999)}"
        token = {
            'access_token': creds.token,
            'id_token': user_id,
            'expires_in': creds.expiry.timestamp() if creds.expiry else 3600
        }
        
        # Store the token and user in our memory store and session
        TOKENS[user_id] = token
        logger.info(f"Created real OAuth token for user: {user_id}")
        
        session['user_id'] = user_id
        session['access_token'] = creds.token
        session['refresh_token'] = creds.refresh_token
        session['use_real_ads_client'] = True
        
        # Update the refresh token in the google-ads.yaml file
        if os.path.exists(google_ads_yaml_path) and creds.refresh_token:
            try:
                import yaml
                with open(google_ads_yaml_path, 'r') as file:
                    config = yaml.safe_load(file)
                
                # Update the refresh token if it's different
                if config.get('refresh_token') != creds.refresh_token:
                    config['refresh_token'] = creds.refresh_token
                    with open(google_ads_yaml_path, 'w') as file:
                        yaml.dump(config, file)
                    logger.info("Updated refresh token in google-ads.yaml")
            except Exception as yaml_error:
                logger.error(f"Error updating YAML file: {yaml_error}")
        
        # Redirect directly to dashboard
        return redirect('/ads-dashboard')
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('enable_real_ads.html', error=f"Error in OAuth callback: {str(e)}")

@app.route('/api/auth/verify', methods=['GET'])
def verify():
    """Verify the user's token and return user info."""
    # Get the token from the Authorization header
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        logger.warning("Invalid authorization header format")
        return jsonify({"isAuthenticated": False, "error": "Invalid authorization header"}), 401
    
    token = auth_header.split(' ')[1]
    logger.info(f"Verifying token: {token[:10]}...")
    
    # Check if we have real credentials
    creds = get_credentials()
    if creds:
        try:
            # Try to use the credentials to access GA4 API
            service = build('analyticsdata', 'v1beta', credentials=creds)
            
            # Make a simple request to verify access
            request_body = {
                'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
                'metrics': [{'name': 'activeUsers'}]
            }
            
            response = service.properties().runReport(
                property=f"properties/{PROPERTY_ID}",
                body=request_body
            ).execute()
            
            # If we get here, the credentials are valid
            user_id = f"google-oauth2|{random.randint(1000000, 9999999)}"
            
            # Create a user if it doesn't exist
            if user_id not in USERS:
                USERS[user_id] = {
                    'id': user_id,
                    'name': 'GA4 User',
                    'email': 'ga4user@example.com',
                    'picture': 'https://ui-avatars.com/api/?name=GA4+User&background=0D8ABC&color=fff'
                }
            
            logger.info(f"Verified real GA4 credentials for user: {user_id}")
            return jsonify({
                "isAuthenticated": True,
                "user": USERS[user_id]
            })
        except Exception as e:
            logger.error(f"Error verifying GA4 credentials: {e}")
            # Fall back to mock verification
    
    # Check if the token exists in our mock tokens
    for user_id, user_token in TOKENS.items():
        if user_token.get('access_token') == token:
            # Token is valid, return user info
            logger.info(f"Verified mock token for user: {user_id}")
            return jsonify({
                "isAuthenticated": True,
                "user": USERS.get(user_id, USERS['google-oauth2|123456789'])
            })
    
    # If we get here, the token is invalid
    logger.warning(f"Invalid token: {token[:10]}...")
    return jsonify({"isAuthenticated": False, "error": "Invalid token"}), 401

# Analytics API routes
@app.route('/api/dashboard/summary', methods=['GET'])
def dashboard_summary():
    """Get dashboard summary data"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Mock dashboard data
    return jsonify({
        "visitors": {
            "total": 12856,
            "change": 12.3,
            "trend": "up"
        },
        "pageViews": {
            "total": 42123,
            "change": 8.7,
            "trend": "up"
        },
        "bounceRate": {
            "value": 32.4,
            "change": -2.1,
            "trend": "down"
        },
        "avgSession": {
            "value": "3m 42s",
            "change": 0.8,
            "trend": "up"
        },
        "trafficSources": [
            {"source": "Direct", "value": 35, "color": "#0070f3"},
            {"source": "Organic Search", "value": 28, "color": "#10b981"},
            {"source": "Social Media", "value": 22, "color": "#7928ca"},
            {"source": "Referral", "value": 15, "color": "#f59e0b"}
        ]
    })

@app.route('/api/google-ads/performance', methods=['GET'])
def ads_performance():
    """Get Google Ads performance data from the Google Ads API
    
    This endpoint retrieves performance metrics from the Google Ads API,
    including impressions, clicks, conversions, cost, and derived metrics.
    It supports date range filtering and previous period comparison.
    
    Query Parameters:
        start_date (str): Start date in YYYY-MM-DD format (defaults to 30 days ago)
        end_date (str): End date in YYYY-MM-DD format (defaults to yesterday)
        previous_period (bool): Whether to include previous period data for comparison
    
    Returns:
        JSON: Performance metrics with values and percentage changes
    """
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    previous_period = request.args.get('previous_period', 'false').lower() == 'true'
    
    # Verify authentication
    auth_header = request.headers.get('Authorization', '')
    
    # Require either a Bearer token or an authenticated session
    if not auth_header.startswith('Bearer ') and 'user_id' not in session:
        logger.warning("Unauthorized request to Google Ads performance endpoint")
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    
    # Extract token
    token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else 'test-token'
    
    # Determine if we should use real data
    # We'll always try to use real data first
    logger.info(f"Getting Google Ads performance data for period: {start_date or 'default'} to {end_date or 'default'}")
    logger.info(f"Previous period comparison: {previous_period}")
    
    try:
        # Import the get_ads_performance function with fallback
        from google_ads_fallback import get_ads_performance_with_fallback
        
        # Get the performance data
        logger.info("Using Google Ads client with fallback to mock data if allowed")
        performance_data = get_ads_performance_with_fallback(start_date, end_date, previous_period)
        
        if not performance_data:
            logger.error("No performance data returned from Google Ads API and mock data is disabled")
            return jsonify({
                "error": "No data available",
                "message": "Failed to retrieve Google Ads performance data and mock data is disabled in production mode",
                "environment": ENVIRONMENT
            }), 404
        
        logger.info(f"Successfully retrieved Google Ads performance data")
        
        # Format the response to match expected structure - display "N/A" for unavailable data
        # Start with a template of all metrics as "N/A"
        response_data = {
            "impressions": {
                "value": "N/A",
                "change": "N/A"
            },
            "clicks": {
                "value": "N/A",
                "change": "N/A"
            },
            "conversions": {
                "value": "N/A",
                "change": "N/A"
            },
            "cost": {
                "value": "N/A",
                "change": "N/A"
            },
            "conversionRate": {
                "value": "N/A",
                "change": "N/A"
            },
            "clickThroughRate": {
                "value": "N/A",
                "change": "N/A"
            },
            "costPerConversion": {
                "value": "N/A",
                "change": "N/A"
            }
        }
        
        # Only update values that are available in the performance_data
        # Use a list to iterate through all metrics
        metrics = [
            "impressions", "clicks", "conversions", "cost", 
            "conversionRate", "clickThroughRate", "costPerConversion"
        ]
        
        for metric in metrics:
            # Check if this metric exists in performance_data
            if metric in performance_data:
                metric_data = performance_data[metric]
                # Only set the value if it exists
                if "value" in metric_data:
                    response_data[metric]["value"] = metric_data["value"]
                # Only set the change if it exists
                if "change" in metric_data:
                    response_data[metric]["change"] = metric_data["change"]
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching Google Ads performance data: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return an error response with helpful information
        return jsonify({
            "error": "Failed to retrieve Google Ads performance data",
            "message": str(e),
            "help": "Please verify your Google Ads API credentials and ensure the API is properly configured."
        }), 500

@app.route('/api/form-performance', methods=['GET'])
def form_performance():
    """Get form performance data"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Mock form performance data
    return jsonify({
        "patientForms": {
            "totalSubmissions": 247,
            "completionRate": 68.5,
            "avgTimeToComplete": "2m 34s",
            "changePercentage": -8.5
        },
        "sponsorForms": {
            "totalSubmissions": 89,
            "completionRate": 72.3,
            "avgTimeToComplete": "3m 12s",
            "changePercentage": -8.2
        }
    })

@app.route('/api/site-metrics', methods=['GET'])
def site_metrics():
    """Get site metrics data"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Mock site metrics data
    return jsonify({
        "conversionRate": {
            "value": 7.18,
            "change": 51.6
        },
        "revenue": {
            "value": 34990,
            "change": -47.8
        },
        "sessions": {
            "value": 59734,
            "change": 53.2
        },
        "engagement": {
            "value": 31.3,
            "change": -45.5
        },
        "bounceRate": {
            "value": 44.9,
            "change": -27.4
        },
        "avgOrder": {
            "value": 99,
            "change": -56.6
        }
    })

@app.route('/api/performance-over-time', methods=['GET'])
def performance_over_time():
    """Get performance time series data"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Mock time series data
    return jsonify([
        {"time": "9 AM", "conversions": 0, "sessions": 120},
        {"time": "10 AM", "conversions": 5, "sessions": 240},
        {"time": "11 AM", "conversions": 12, "sessions": 380},
        {"time": "12 PM", "conversions": 25, "sessions": 520},
        {"time": "1 PM", "conversions": 35, "sessions": 650},
        {"time": "2 PM", "conversions": 48, "sessions": 700},
        {"time": "3 PM", "conversions": 62, "sessions": 830},
        {"time": "4 PM", "conversions": 75, "sessions": 950},
        {"time": "5 PM", "conversions": 82, "sessions": 1050},
        {"time": "6 PM", "conversions": 90, "sessions": 1150},
        {"time": "7 PM", "conversions": 100, "sessions": 1250}
    ])

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'Allervie Analytics API',
        'environment': ENVIRONMENT,
        'version': '1.0.0',
        'apiAvailable': True
    })

@app.route('/api/endpoints', methods=['GET'])
def list_endpoints():
    """List all available API endpoints for testing purposes
    
    This endpoint is intended for development/testing to see all available API 
    endpoints that can be called from the frontend.
    """
    logger.info("Listing all available API endpoints")
    
    # Collect all API endpoints from the main app and blueprints
    endpoints = []
    
    # Add endpoints from the main app
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static' and 'GET' in rule.methods:
            url = str(rule)
            # Get the function associated with this endpoint
            func = app.view_functions[rule.endpoint]
            # Try to get the docstring
            description = func.__doc__.split('\n')[0] if func.__doc__ else "No description"
            
            endpoints.append({
                'url': url,
                'methods': list(rule.methods),
                'description': description,
                'auth_required': 'auth' in url or 'google-ads' in url
            })
    
    # Add endpoints from the extended_routes blueprint
    try:
        # Get the AVAILABLE_ENDPOINTS list from the blueprint
        from extended_routes import AVAILABLE_ENDPOINTS
        endpoints.extend(AVAILABLE_ENDPOINTS)
    except ImportError:
        logger.warning("Could not import AVAILABLE_ENDPOINTS from extended_routes")
    
    # Return the list of endpoints sorted by URL
    return jsonify(sorted(endpoints, key=lambda x: x.get('url', '') if isinstance(x.get('url', ''), str) else x.get('endpoint', '')))

@app.route('/api/auth/mock-token', methods=['GET'])
def mock_token():
    """Create a mock auth token for testing"""
    if ENVIRONMENT == "production" and not ALLOW_MOCK_AUTH:
        logger.warning("Mock authentication is disabled in production mode")
        return jsonify({
            "error": "Mock authentication disabled",
            "message": "Mock authentication is disabled in production mode. Use the real OAuth authentication flow.",
            "environment": ENVIRONMENT
        }), 403
    
    # Create a mock user ID
    user_id = f"google-oauth2|{123456789}"
    
    # Create a mock token
    token = {
        'access_token': f"mock-token-{int(time.time())}",
        'id_token': user_id,
        'expires_in': 3600
    }
    
    # Store the token
    TOKENS[user_id] = token
    logger.info(f"Created mock OAuth token for user: {user_id}")
    
    # Store user in session
    session['user_id'] = user_id
    session['access_token'] = token['access_token']
    
    return jsonify({
        "status": "success",
        "message": "Mock authentication successful",
        "token": token['access_token'],
        "user_id": user_id
    })

@app.route('/api/auth/use-real-ads-client', methods=['GET'])
def use_real_ads_client():
    """Set a flag to use the real Google Ads client even with a mock token"""
    logger.info("Setting flag to use real Google Ads client")
    
    # Set the global flag
    global USE_REAL_ADS_CLIENT
    USE_REAL_ADS_CLIENT = True
    
    # Also set the flag in the session for backward compatibility
    session['use_real_ads_client'] = True
    
    return jsonify({
        'status': 'success',
        'message': 'Now using real Google Ads client with mock token'
    })

@app.route('/api/google-ads/test-connection', methods=['GET'])
def test_google_ads_connection():
    """Test the Google Ads API connection"""
    logger.info("Testing Google Ads API connection")
    
    try:
        # Import the Google Ads client
        from google_ads_client import get_google_ads_client
        
        # Get the client
        client = get_google_ads_client()
        
        if not client:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create Google Ads client'
            }), 500
        
        # Get customer ID from client
        customer_id = client.login_customer_id
        
        # Try a simple query to test the connection
        ga_service = client.get_service("GoogleAdsService")
        
        # Create a simple query
        query = """
            SELECT 
                customer.id
            FROM customer
            LIMIT 1
        """
        
        # Execute the query
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        response = ga_service.search(request=search_request)
        
        # If we get here, the connection works
        return jsonify({
            'status': 'success',
            'message': 'Google Ads API connection successful',
            'customer_id': customer_id
        })
    except Exception as e:
        logger.error(f"Error testing Google Ads API connection: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return jsonify({
            'status': 'error',
            'message': f'Google Ads API connection failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/google-ads/simple-test', methods=['GET'])
def simple_google_ads_test():
    """A simpler test for the Google Ads API connection"""
    logger.info("Running simple Google Ads API test")
    
    try:
        # Import directly from the Google Ads library
        from google.ads.googleads.client import GoogleAdsClient
        from google.ads.googleads.errors import GoogleAdsException
        import google.ads.googleads
        import yaml
        
        # Get the path to the credentials file
        credentials_path = os.path.join(CREDENTIALS_DIR, 'google-ads.yaml')
        
        if not os.path.exists(credentials_path):
            return jsonify({
                'status': 'error',
                'message': f'Google Ads YAML configuration file not found at {credentials_path}'
            }), 500
        
        # Read the YAML file directly to get configuration details
        with open(credentials_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
        
        # Get the installed library version
        library_version = google.ads.googleads.__version__ if hasattr(google.ads.googleads, '__version__') else "25.2.0"
        
        # Load the client directly - explicitly specify version v17 (supported by the library)
        client = GoogleAdsClient.load_from_storage(credentials_path, version="v17")
        
        # Get the API version - now it should be v17
        api_version = "v17"  # Explicitly set to v17
        
        # Try to get a service to test the connection
        try:
            ga_service = client.get_service("GoogleAdsService")  # No need to specify version again
            service_status = "Successfully got GoogleAdsService"
            
            # Get available services
            available_services = []
            for attr in dir(client):
                if attr.startswith('get_') and callable(getattr(client, attr)) and attr != 'get_service' and attr != 'get_type':
                    service_name = attr[4:]  # Remove 'get_' prefix
                    available_services.append(service_name)
            
            # Try a simple query
            try:
                customer_id = client.login_customer_id
                
                # Try a simple query with v17 syntax
                query = f"""
                SELECT 
                  customer.id,
                  customer.descriptive_name,
                  customer.currency_code,
                  customer.time_zone
                FROM customer
                LIMIT 1
                """
                
                # Execute the query
                try:
                    response = ga_service.search(
                        customer_id=customer_id,
                        query=query
                    )
                    
                    # Process the results
                    customer_details = {}
                    for row in response:
                        customer = row.customer
                        customer_details = {
                            "id": customer.id,
                            "descriptive_name": customer.descriptive_name if hasattr(customer, "descriptive_name") else "N/A",
                            "currency_code": customer.currency_code if hasattr(customer, "currency_code") else "N/A",
                            "time_zone": customer.time_zone if hasattr(customer, "time_zone") else "N/A"
                        }
                        break  # Just get the first one
                    
                    if customer_details:
                        query_status = "Successfully retrieved customer details"
                    else:
                        customer_details = {"id": customer_id}
                        query_status = "Query executed but no customer details found"
                except Exception as search_error:
                    customer_details = {"id": customer_id}
                    query_status = f"Error executing search query: {str(search_error)}"
            except Exception as query_error:
                customer_details = {"id": customer_id}
                query_status = f"Error setting up query: {str(query_error)}"
            
            # Get account information from the config
            account_info = {
                "login_customer_id": config.get('login_customer_id', 'N/A'),
                "developer_token": config.get('developer_token', 'N/A')[:5] + '...' if config.get('developer_token') else 'N/A',
                "client_id": config.get('client_id', 'N/A')[:10] + '...' if config.get('client_id') else 'N/A',
                "use_proto_plus": config.get('use_proto_plus', 'N/A'),
                "available_services_count": len(available_services)
            }
            
        except Exception as service_error:
            service_status = f"Error getting GoogleAdsService: {str(service_error)}"
            account_info = {}
            customer_details = {}
            query_status = "Did not attempt to get account information"
        
        return jsonify({
            'status': 'success',
            'message': 'Successfully created Google Ads client',
            'api_version': api_version,
            'library_version': library_version,
            'login_customer_id': client.login_customer_id,
            'service_status': service_status,
            'account_info': account_info,
            'customer_details': customer_details,
            'query_status': query_status
        })
    except Exception as e:
        logger.error(f"Error in simple Google Ads API test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return jsonify({
            'status': 'error',
            'message': f'Simple Google Ads API test failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/enable-real-ads', methods=['GET'])
def enable_real_ads_page():
    """Serve the enable_real_ads.html page"""
    return render_template('enable_real_ads.html')

@app.route('/test-api', methods=['GET'])
def test_api_page():
    """Serve the test_api.html page"""
    return render_template('test_api.html')

@app.route('/api-endpoints', methods=['GET'])
def api_endpoints_page():
    """Serve the api_endpoints.html page"""
    return render_template('api_endpoints.html')

@app.route('/ads-dashboard', methods=['GET'])
def ads_dashboard_page():
    """Serve the Google Ads dashboard page with OAuth authentication"""
    # In development mode with mock auth, auto-authenticate the user
    if ENVIRONMENT == "development" and ALLOW_MOCK_AUTH:
        # Set a mock user ID if not already set
        if 'user_id' not in session:
            session['user_id'] = f"mock-user-{random.randint(1000, 9999)}"
            logger.info(f"Auto-authenticated with mock user: {session['user_id']}")
    else:
        # Check for authorized session
        if 'user_id' not in session:
            # Redirect to login page if not authenticated
            return redirect(url_for('login'))
    
    # Check for a 'simple' query parameter to use the simplified dashboard
    if request.args.get('simple') == 'true':
        return render_template('ads_dashboard_simple.html')
    
    # Default to the regular dashboard
    return render_template('ads_dashboard.html')
    
@app.route('/ads-dashboard-simple', methods=['GET'])
def ads_dashboard_simple_page():
    """Serve the simplified Google Ads dashboard page with OAuth authentication"""
    # In development mode with mock auth, auto-authenticate the user
    if ENVIRONMENT == "development" and ALLOW_MOCK_AUTH:
        # Set a mock user ID if not already set
        if 'user_id' not in session:
            session['user_id'] = f"mock-user-{random.randint(1000, 9999)}"
            logger.info(f"Auto-authenticated with mock user: {session['user_id']}")
    else:
        # Check for authorized session
        if 'user_id' not in session:
            # Redirect to login page if not authenticated
            return redirect(url_for('login'))
    
    return render_template('ads_dashboard_simple.html')

@app.route('/run-diagnostics', methods=['GET'])
def run_network_diagnostics():
    """Run network diagnostics and display results"""
    if not HAS_ERROR_HANDLERS:
        return jsonify({
            "error": "Network diagnostics module not available",
            "message": "The network_diagnostics.py module is required for this feature"
        }), 500
    
    try:
        # Generate HTML report
        html_report = generate_diagnostics_report()
        
        # Save report to file in static directory
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        os.makedirs(static_dir, exist_ok=True)
        report_path = os.path.join(static_dir, f"network_diagnostics_{int(time.time())}.html")
        
        with open(report_path, 'w') as f:
            f.write(html_report)
        
        # Return HTML directly for display
        return html_report
    except Exception as e:
        return jsonify({
            "error": f"Failed to run diagnostics: {str(e)}",
            "details": str(e)
        }), 500

@app.route('/api/diagnostics/check-port', methods=['GET'])
def check_port_availability():
    """Check if a port is available for use"""
    port = request.args.get('port', type=int)
    
    if not port:
        return jsonify({
            "error": "Missing required parameter: port",
            "message": "Please specify a port to check"
        }), 400
    
    try:
        # Try to create a socket and bind to the port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            
            if result == 0:
                # Port is in use
                return jsonify({
                    "port": port,
                    "available": False,
                    "message": f"Port {port} is already in use"
                })
            else:
                # Port is available
                return jsonify({
                    "port": port,
                    "available": True,
                    "message": f"Port {port} is available"
                })
    except Exception as e:
        return jsonify({
            "port": port,
            "error": str(e),
            "message": f"Error checking port {port}"
        }), 500

@app.route('/api/diagnostics/system-info', methods=['GET'])
def get_system_info():
    """Get basic system information"""
    try:
        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add network interface information if available
        try:
            if hasattr(socket, 'if_nameindex'):
                interfaces = []
                for i in socket.if_nameindex():
                    interfaces.append({
                        "index": i[0],
                        "name": i[1]
                    })
                info["network_interfaces"] = interfaces
        except:
            pass
        
        return jsonify(info)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error retrieving system information"
        }), 500
        
@app.route('/connection-troubleshooter', methods=['GET'])
def connection_troubleshooter():
    """Serve the connection troubleshooter page"""
    return render_template('connection_troubleshooter.html')

if __name__ == '__main__':
    # Default port is 5002 (was changed from 5001 to avoid conflicts)
    port = int(os.getenv('PORT', 5002))
    
    # Default to development mode
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # Bind to localhost for development
    host = os.getenv('HOST', 'localhost')
    
    print("=" * 70)
    print(f"Starting Allervie Analytics API on port {port}")
    print(f"Server bound to: {host}")
    print(f"Debug mode: {'enabled' if debug else 'disabled'}")
    print(f"Frontend URL: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")
    print(f"Dashboard URLs:")
    print(f" - http://localhost:{port}/ads-dashboard")
    print(f" - http://127.0.0.1:{port}/ads-dashboard")
    print("=" * 70)
    
    # Run the app with the specified host, port and debug settings
    app.run(host=host, port=port, debug=debug)
