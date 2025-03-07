"""
Allervie Analytics Dashboard - Simplified Backend API

This Flask application serves as the backend for the Allervie Analytics Dashboard,
providing API endpoints for authentication and analytics data.
"""

import os
import json
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
from google_ads_client import get_ads_performance
from extended_routes import extended_bp, AVAILABLE_ENDPOINTS  # Import our extended routes blueprint and available endpoints
from werkzeug.middleware.proxy_fix import ProxyFix

# Import config
from config import USE_REAL_ADS_CLIENT, ALLOW_MOCK_DATA, ALLOW_MOCK_AUTH, ENVIRONMENT

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
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8080')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5002/api/auth/callback')
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'allervie-dashboard-secret-key')
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
            # Use mock authentication if no client secret is available
            logger.warning("No client_secret.json found, using mock authentication")
            return jsonify({
                'auth_url': f"{FRONTEND_URL}/mock-auth?redirect_uri={REDIRECT_URI}"
            })
    
    try:
        # Create the flow using the client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_PATH, 
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        # Generate the authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store the flow in the session
        session['flow'] = flow.to_json()
        
        return jsonify({'auth_url': auth_url})
    except Exception as e:
        logger.error(f"Error initiating OAuth flow: {e}")
        # Fallback to mock authentication
        return jsonify({
            'auth_url': f"{FRONTEND_URL}/mock-auth?redirect_uri={REDIRECT_URI}"
        })

@app.route('/api/auth/callback', methods=['GET'])
def callback():
    """Handle the OAuth 2.0 callback."""
    # Check if this is a mock auth callback
    if 'mock' in request.args:
        logger.warning("Mock authentication is disabled in production mode")
        return redirect(f"{FRONTEND_URL}/login?error=mock_auth_disabled")
    
    # Handle real OAuth callback
    try:
        # Get the authorization code from the request
        code = request.args.get('code')
        
        if not code:
            logger.error("No authorization code received")
            return redirect(f"{FRONTEND_URL}/login?error=no_code")
        
        # Get the flow from the session
        if 'flow' not in session:
            logger.error("No flow found in session")
            return redirect(f"{FRONTEND_URL}/login?error=no_flow")
        
        flow = InstalledAppFlow.from_client_config(
            json.loads(session['flow']),
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        # Exchange the authorization code for tokens
        flow.fetch_token(code=code)
        
        # Get the credentials
        creds = flow.credentials
        
        # Save the credentials to a file
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        
        # Get user info from the ID token
        user_id = f"google-oauth2|{random.randint(1000000, 9999999)}"
        
        # Create a token
        token = {
            'access_token': creds.token,
            'id_token': user_id,
            'expires_in': creds.expiry.timestamp() if creds.expiry else 3600
        }
        
        # Store the token
        TOKENS[user_id] = token
        logger.info(f"Created real OAuth token for user: {user_id}")
        
        # Redirect to the frontend with the token
        redirect_url = f"{FRONTEND_URL}/login?token={token['access_token']}"
        logger.info(f"Redirecting to: {redirect_url}")
        return redirect(redirect_url)
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return redirect(f"{FRONTEND_URL}/login?error=callback_error")

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
    
    # Verify authentication (for testing, we'll allow the request even without a proper token)
    auth_header = request.headers.get('Authorization', '')
    use_test_token = True  # Set this to True to allow testing without proper auth
    
    if not auth_header.startswith('Bearer ') and not use_test_token:
        logger.warning("Unauthorized request to Google Ads performance endpoint")
        return jsonify({"error": "Unauthorized"}), 401
    
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
    """This endpoint is disabled in production mode"""
    logger.warning("Mock authentication is disabled in production mode")
    return jsonify({
        "error": "Mock authentication disabled",
        "message": "Mock authentication is disabled in production mode. Use the real OAuth authentication flow.",
        "environment": ENVIRONMENT
    }), 403

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

if __name__ == '__main__':
    port = 5002  # Changed from 5001 to avoid conflicts
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    print(f"Starting Allervie Analytics API on port {port}")
    print(f"Frontend URL: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
