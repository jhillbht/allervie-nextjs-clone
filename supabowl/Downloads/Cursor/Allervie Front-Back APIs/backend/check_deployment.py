#!/usr/bin/env python
"""
Deployment Check Script for Allervie Analytics Dashboard

This script validates the configuration and checks that the OAuth token is valid
and properly refreshing. It's designed to help diagnose issues with the
DigitalOcean deployment.
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import Google Ads libraries
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    HAS_GOOGLE_ADS = True
    logger.info("Successfully imported Google Ads libraries")
except ImportError:
    HAS_GOOGLE_ADS = False
    logger.error("Failed to import Google Ads libraries")

def check_google_ads_yaml():
    """Check if google-ads.yaml file exists and is valid"""
    possible_paths = [
        Path(__file__).parent.parent / "credentials" / "google-ads.yaml",
        Path(__file__).parent / "google-ads.yaml",
        Path.cwd() / "credentials" / "google-ads.yaml",
        Path.cwd() / "google-ads.yaml",
    ]
    
    for path in possible_paths:
        if path.exists():
            try:
                import yaml
                with open(path, 'r') as f:
                    config = yaml.safe_load(f)
                    logger.info(f"Found Google Ads config at {path}")
                    
                    # Check required fields
                    required_fields = ['client_id', 'client_secret', 'developer_token', 'login_customer_id', 'refresh_token']
                    missing_fields = [field for field in required_fields if not config.get(field)]
                    
                    if missing_fields:
                        logger.error(f"Missing required fields in google-ads.yaml: {missing_fields}")
                        return False, path, missing_fields
                    
                    # Print info about the config
                    logger.info(f"YAML config contains login_customer_id: {config.get('login_customer_id', 'Not Found')}")
                    logger.info(f"YAML config contains api_version: {config.get('api_version', 'Not Found')}")
                    logger.info(f"YAML config contains use_proto_plus: {config.get('use_proto_plus', 'Not Found')}")
                    
                    return True, path, config
            except Exception as e:
                logger.error(f"Error reading YAML file {path}: {e}")
                return False, path, str(e)
    
    logger.error("No Google Ads YAML file found")
    return False, None, "No Google Ads YAML file found"

def check_token_validity():
    """Verify if the refresh token is valid by attempting to get an access token"""
    if not HAS_GOOGLE_ADS:
        logger.error("Google Ads libraries not available")
        return False, "Google Ads libraries not available"
    
    # First check if the YAML file exists and is valid
    yaml_valid, yaml_path, yaml_result = check_google_ads_yaml()
    if not yaml_valid:
        return False, f"Invalid YAML configuration: {yaml_result}"
    
    try:
        # Load configuration
        if isinstance(yaml_result, dict):
            config = yaml_result
        else:
            import yaml
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
        
        # Create client using the YAML file
        try:
            api_version = config.get('api_version', 'v17')
            client = GoogleAdsClient.load_from_storage(yaml_path, version=api_version)
            logger.info(f"Created Google Ads client with API version {api_version}")
            
            # Test the client with a simple query
            ga_service = client.get_service("GoogleAdsService")
            customer_id = config['login_customer_id']
            
            # Simple query to verify token works
            query = """
                SELECT customer.id
                FROM customer
                LIMIT 1
            """
            
            response = ga_service.search(
                customer_id=customer_id,
                query=query
            )
            
            # Process response to confirm it worked
            for row in response:
                logger.info(f"Successfully verified token with customer ID: {row.customer.id}")
                return True, f"Token is valid for customer ID: {row.customer.id}"
            
            # If we get here with no rows, the query was successful but returned no data
            return True, "Token is valid but query returned no results"
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex}")
            error_details = []
            for error in ex.failure.errors:
                error_details.append(f"Error with message: {error.message}")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        error_details.append(f"On field: {field_path_element.field_name}")
            
            return False, "Google Ads API error: " + "; ".join(error_details)
        except Exception as e:
            logger.error(f"Error creating Google Ads client: {e}")
            logger.error(traceback.format_exc())
            return False, f"Error creating Google Ads client: {str(e)}"
    except Exception as e:
        logger.error(f"Error checking token validity: {e}")
        logger.error(traceback.format_exc())
        return False, f"Error checking token validity: {str(e)}"

def check_token_expiry():
    """Check when the current token will expire"""
    # First check if token.json exists
    token_paths = [
        Path(__file__).parent.parent / "credentials" / "token.json",
        Path(__file__).parent / "token.json",
        Path.cwd() / "credentials" / "token.json",
        Path.cwd() / "token.json",
    ]
    
    for path in token_paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    token_data = json.load(f)
                    
                    # Check if token and refresh_token exist
                    if 'token' not in token_data:
                        logger.error(f"No access token found in {path}")
                        return False, f"No access token found in {path}"
                    
                    if 'refresh_token' not in token_data:
                        logger.error(f"No refresh token found in {path}")
                        return False, f"No refresh token found in {path}"
                    
                    # Check if expiry info exists
                    # Note: Google OAuth tokens typically expire after 1 hour
                    # The refresh_token doesn't expire unless revoked or unused for an extended period
                    logger.info(f"Found token.json at {path}")
                    logger.info(f"Access token: {token_data['token'][:10]}...")
                    logger.info(f"Refresh token: {token_data['refresh_token'][:10]}...")
                    
                    return True, "Token file exists with both access and refresh tokens"
            except Exception as e:
                logger.error(f"Error reading token file {path}: {e}")
                return False, f"Error reading token file: {str(e)}"
    
    logger.error("No token.json file found")
    return False, "No token.json file found"

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = [
        'GOOGLE_ADS_CLIENT_ID',
        'GOOGLE_ADS_CLIENT_SECRET',
        'GOOGLE_ADS_DEVELOPER_TOKEN',
        'GOOGLE_ADS_LOGIN_CUSTOMER_ID',
        'GOOGLE_ADS_REFRESH_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False, f"Missing required environment variables: {missing_vars}"
    
    # Log some non-sensitive parts of the environment variables
    logger.info(f"GOOGLE_ADS_CLIENT_ID: {os.environ.get('GOOGLE_ADS_CLIENT_ID', '')[:10]}...")
    logger.info(f"GOOGLE_ADS_LOGIN_CUSTOMER_ID: {os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')}")
    
    return True, "All required environment variables are set"

def check_config_settings():
    """Check the settings in config.py"""
    try:
        from config import (
            ENVIRONMENT, 
            ALLOW_MOCK_DATA, 
            USE_REAL_ADS_CLIENT,
            CLIENT_CUSTOMER_ID
        )
        
        logger.info(f"ENVIRONMENT: {ENVIRONMENT}")
        logger.info(f"ALLOW_MOCK_DATA: {ALLOW_MOCK_DATA}")
        logger.info(f"USE_REAL_ADS_CLIENT: {USE_REAL_ADS_CLIENT}")
        logger.info(f"CLIENT_CUSTOMER_ID: {CLIENT_CUSTOMER_ID}")
        
        # Check if the configuration is appropriate for production
        if ENVIRONMENT == "production":
            if ALLOW_MOCK_DATA:
                logger.warning("ALLOW_MOCK_DATA is True in production environment")
            if not USE_REAL_ADS_CLIENT:
                logger.warning("USE_REAL_ADS_CLIENT is False in production environment")
        
        return True, "Config settings loaded successfully"
    except ImportError as e:
        logger.warning(f"Could not import config settings: {e}")
        return False, f"Could not import config settings: {e}"
    except Exception as e:
        logger.error(f"Error checking config settings: {e}")
        return False, f"Error checking config settings: {e}"

def check_api_endpoints():
    """Test API endpoints for data retrieval"""
    try:
        # Import the necessary functions for API testing
        from extended_google_ads_api import get_campaign_performance
        
        # Try to get campaign performance data
        campaigns = get_campaign_performance()
        
        if campaigns:
            logger.info(f"Successfully retrieved {len(campaigns)} campaigns")
            
            # Log some campaign info
            for i, campaign in enumerate(campaigns[:3]):  # Show first 3 campaigns
                logger.info(f"Campaign {i+1}: {campaign.get('name', 'Unknown')} - {campaign.get('status', 'Unknown')}")
            
            if len(campaigns) > 3:
                logger.info(f"... and {len(campaigns) - 3} more campaigns")
            
            return True, f"Successfully retrieved {len(campaigns)} campaigns"
        else:
            logger.error("No campaign data returned")
            return False, "No campaign data returned"
    except Exception as e:
        logger.error(f"Error checking API endpoints: {e}")
        logger.error(traceback.format_exc())
        return False, f"Error checking API endpoints: {e}"

def main():
    """Run all checks and print a summary"""
    print("\n===== Allervie Analytics Deployment Check =====\n")
    
    # Check if Google Ads libraries are available
    if HAS_GOOGLE_ADS:
        print("✅ Google Ads libraries available")
    else:
        print("❌ Google Ads libraries not found")
    
    # Run all checks
    print("\n----- Configuration Checks -----")
    yaml_valid, yaml_path, yaml_result = check_google_ads_yaml()
    if yaml_valid:
        print(f"✅ Google Ads YAML is valid: {yaml_path}")
    else:
        print(f"❌ Google Ads YAML issue: {yaml_result}")
    
    env_valid, env_message = check_env_vars()
    if env_valid:
        print(f"✅ Environment variables: {env_message}")
    else:
        print(f"❌ Environment variables: {env_message}")
    
    config_valid, config_message = check_config_settings()
    if config_valid:
        print(f"✅ Config settings: {config_message}")
    else:
        print(f"❌ Config settings: {config_message}")
    
    print("\n----- OAuth Token Checks -----")
    token_valid, token_message = check_token_validity()
    if token_valid:
        print(f"✅ Token validity: {token_message}")
    else:
        print(f"❌ Token validity: {token_message}")
    
    token_expiry_valid, token_expiry_message = check_token_expiry()
    if token_expiry_valid:
        print(f"✅ Token file: {token_expiry_message}")
    else:
        print(f"❌ Token file: {token_expiry_message}")
    
    print("\n----- API Data Retrieval Checks -----")
    api_valid, api_message = check_api_endpoints()
    if api_valid:
        print(f"✅ API endpoints: {api_message}")
    else:
        print(f"❌ API endpoints: {api_message}")
    
    print("\n----- Recommendations -----")
    recommendations = []
    
    if not yaml_valid:
        recommendations.append("- Fix the google-ads.yaml configuration file")
    
    if not env_valid:
        recommendations.append("- Set the missing environment variables in Digital Ocean App Platform")
    
    if not token_valid:
        recommendations.append("- Generate a new refresh token using oauth_server.py")
        recommendations.append("- Update both google-ads.yaml and the GOOGLE_ADS_REFRESH_TOKEN environment variable")
    
    if not api_valid:
        recommendations.append("- Check API access and permissions in the Google Ads API Center")
        recommendations.append("- Verify the developer token has access to the client account")
    
    if config_valid and not recommendations:
        try:
            from config import ENVIRONMENT, ALLOW_MOCK_DATA
            if ENVIRONMENT == "production" and ALLOW_MOCK_DATA:
                recommendations.append("- Set ALLOW_MOCK_DATA = False in config.py for production use")
        except:
            pass
    
    if recommendations:
        for recommendation in recommendations:
            print(recommendation)
    else:
        print("- Your deployment looks good! No specific recommendations.")
    
    print("\n============================================\n")

if __name__ == "__main__":
    main()