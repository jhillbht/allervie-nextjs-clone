"""
Google Ads API Integration Module for the Allervie Analytics Dashboard.

This module provides functions to seamlessly integrate the Google Ads API
with the dashboard application, including automatic token management.
"""

import os
import logging
from pathlib import Path
import json
from flask import current_app
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google_ads_client import get_google_ads_client  # Import the centralized client initialization

# Import the smart token manager
from smart_token_manager import verify_ads_token

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('app_ads_integration')

def get_google_ads_client(force_token_refresh=False):
    """
    Get a configured Google Ads API client with automatic token management.
    
    This function:
    1. Verifies token validity before creating the client
    2. Refreshes the token if necessary using the smart token manager
    3. Returns a fully configured Google Ads client
    
    Args:
        force_token_refresh (bool): Force refresh of the token regardless of validity
        
    Returns:
        GoogleAdsClient: A configured Google Ads API client
        None: If client creation fails
    """
    try:
        # Verify token validity before creating client
        if not verify_ads_token(force_refresh=force_token_refresh):
            logger.error("Failed to verify Google Ads API token")
            return None
        
        # Get credentials file path
        credentials_path = Path(__file__).parent.parent / "credentials" / "google-ads.yaml"
        
        if not credentials_path.exists():
            logger.error(f"Google Ads YAML configuration file not found at {credentials_path}")
            return None
        
        logger.info(f"Loading Google Ads client from {credentials_path}")
        
        # Create the client
        client = GoogleAdsClient.load_from_storage(str(credentials_path))
        logger.info("Successfully loaded Google Ads client")
        
        return client
    
    except Exception as e:
        logger.error(f"Error creating Google Ads client: {e}")
        return None

def get_ads_performance(start_date=None, end_date=None, previous_period=False):
    """
    Fetch performance metrics from Google Ads API with automatic token management.
    
    This function wraps the original ads performance function with token verification
    to ensure reliable API access.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
        previous_period (bool, optional): If True, fetch data for the previous period.
        
    Returns:
        dict: Performance metrics for the specified period
        None: If the request fails
    """
    # Get client with token verification
    client = get_google_ads_client()
    if not client:
        logger.error("Failed to create Google Ads client")
        return None
    
    try:
        # Get customer ID from client
        customer_id = client.login_customer_id
        logger.info(f"Using customer ID: {customer_id}")
        
        # Create Google Ads query with enhanced metrics for v17 API
        query = f"""
            SELECT 
                metrics.impressions, 
                metrics.clicks, 
                metrics.conversions, 
                metrics.cost_micros,
                metrics.ctr,
                metrics.all_conversions_from_interactions_rate,
                metrics.cost_per_conversion
            FROM campaign
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        logger.debug(f"Query: {query}")
        
        # Execute the query using the v13 API style
        logger.info(f"Getting GoogleAdsService for customer ID: {customer_id}")
        ga_service = client.get_service("GoogleAdsService")
        logger.info("Successfully got GoogleAdsService")
        
        try:
            # Try the v17 search style first
            logger.info(f"Executing search query for dates {start_date} to {end_date}")
            try:
                # Direct parameter style
                logger.info("Executing search with customer_id='{}' using direct parameter style".format(customer_id))
                search_response = ga_service.search(
                    customer_id=customer_id,
                    query=query
                )
                logger.info("Search query executed successfully using direct parameter style")
            except TypeError as type_error:
                # Maybe this version expects different parameters, let's try another approach
                logger.warning(f"TypeError with direct parameter style: {type_error}, trying dictionary style")
                search_response = ga_service.search({
                    'customer_id': customer_id,
                    'query': query
                })
                logger.info("Search query executed successfully using dictionary style")
            
        except Exception as api_error:
            logger.warning(f"Error with v17 search style, trying legacy style: {api_error}")
            # Fall back to legacy style
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            search_response = ga_service.search(request=search_request)
        
        logger.info("Successfully received response from Google Ads API")
        
        # Process the response
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_cost_micros = 0
        
        # For weighted averages of rate metrics
        weighted_ctr_sum = 0
        weighted_conv_rate_sum = 0
        weighted_cost_per_conv_sum = 0
        
        # Track campaigns with data for proper averaging
        campaigns_with_impressions = 0
        campaigns_with_clicks = 0
        campaigns_with_conversions = 0
        
        # Process each row in the response
        row_count = 0
        
        for row in search_response:
            row_count += 1
            metrics = row.metrics
            
            # Aggregate basic metrics
            total_impressions += metrics.impressions
            total_clicks += metrics.clicks
            total_conversions += metrics.conversions
            total_cost_micros += metrics.cost_micros
            
            # Weighted CTR - weight by impressions
            if metrics.impressions > 0:
                campaigns_with_impressions += 1
                weighted_ctr_sum += metrics.ctr * metrics.impressions
            
            # Weighted conversion rate - weight by clicks
            if metrics.clicks > 0:
                campaigns_with_clicks += 1
                weighted_conv_rate_sum += metrics.all_conversions_from_interactions_rate * metrics.clicks
            
            # Weighted cost per conversion - weight by conversions
            if metrics.conversions > 0:
                campaigns_with_conversions += 1
                weighted_cost_per_conv_sum += metrics.cost_per_conversion * metrics.conversions
        
        logger.info(f"Processed {row_count} campaign rows from Google Ads API response")
        
        # Convert cost from micros to dollars
        total_cost = total_cost_micros / 1000000
        
        # Calculate metrics
        # 1. CTR - calculate either as weighted average or direct calculation
        if total_impressions > 0:
            if campaigns_with_impressions > 0:
                ctr = (weighted_ctr_sum / total_impressions) * 100  # Convert to percentage
            else:
                ctr = (total_clicks / total_impressions) * 100
        else:
            ctr = 0
        
        # 2. Conversion rate - calculate either as weighted average or direct calculation
        if total_clicks > 0:
            if campaigns_with_clicks > 0:
                conv_rate = (weighted_conv_rate_sum / total_clicks) * 100  # Convert to percentage
            else:
                conv_rate = (total_conversions / total_clicks) * 100
        else:
            conv_rate = 0
        
        # 3. Cost per conversion - calculate either as weighted average or direct calculation
        if total_conversions > 0:
            if campaigns_with_conversions > 0:
                cost_per_conv = weighted_cost_per_conv_sum / total_conversions
            else:
                cost_per_conv = total_cost / total_conversions
        else:
            cost_per_conv = 0
        
        # Return the metrics in the expected format
        return {
            "impressions": {"value": int(total_impressions), "change": 0},  # Change calculation would need previous period data
            "clicks": {"value": int(total_clicks), "change": 0},
            "conversions": {"value": int(total_conversions), "change": 0},
            "cost": {"value": round(total_cost, 2), "change": 0},
            "conversionRate": {"value": round(conv_rate, 2), "change": 0},
            "clickThroughRate": {"value": round(ctr, 2), "change": 0},
            "costPerConversion": {"value": round(cost_per_conv, 2), "change": 0}
        }
    except Exception as e:
        logger.error(f"Error getting ads performance: {e}")
        logger.error(traceback.format_exc())
        return None

def verify_google_ads_setup():
    """
    Verify the Google Ads API setup.
    
    This function:
    1. Checks for the existence of the YAML configuration file
    2. Verifies token validity
    3. Tests a simple API call
    
    Returns:
        dict: Status information
    """
    status = {
        "yaml_exists": False,
        "token_valid": False,
        "api_accessible": False,
        "customer_found": False,
        "error": None
    }
    
    # Check for YAML file
    credentials_path = Path(__file__).parent.parent / "credentials" / "google-ads.yaml"
    if credentials_path.exists():
        status["yaml_exists"] = True
    
    try:
        # Check token validity and create client
        client = get_google_ads_client()
        
        if client:
            status["token_valid"] = True
            
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
            
            try:
                response = ga_service.search(request=search_request)
                status["api_accessible"] = True
                
                # Check if customer data was returned
                for row in response:
                    if row.customer.id:
                        status["customer_found"] = True
                        break
            
            except GoogleAdsException as ex:
                if ex.error.code().name == "CUSTOMER_NOT_FOUND":
                    status["api_accessible"] = True
                    status["error"] = "Customer ID not found or not accessible"
                else:
                    status["error"] = f"API error: {ex.error.code().name}"
            
            except Exception as e:
                status["error"] = f"API call error: {str(e)}"
    
    except Exception as e:
        status["error"] = f"Setup verification error: {str(e)}"
    
    return status

def integrate_with_app(app):
    """
    Integrate Google Ads API with the Flask application.
    
    This function:
    1. Adds routes for Google Ads API endpoints
    2. Provides API data with automatic token management
    
    Args:
        app: Flask application instance
    """
    @app.route('/api/google-ads/status', methods=['GET'])
    def google_ads_status():
        """
        Get the status of the Google Ads API integration.
        
        Returns:
            dict: Status information
        """
        from flask import jsonify
        status = verify_google_ads_setup()
        return jsonify(status)
    
    @app.route('/api/google-ads/force-refresh', methods=['POST'])
    def force_refresh_token():
        """
        Force refresh of the Google Ads API token.
        
        Returns:
            dict: Result of the token refresh operation
        """
        from flask import jsonify
        
        try:
            success = verify_ads_token(force_refresh=True)
            
            if success:
                return jsonify({"status": "success", "message": "Token refreshed successfully"})
            else:
                return jsonify({"status": "error", "message": "Failed to refresh token"}), 500
        
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error refreshing token: {str(e)}"}), 500

    # Integration complete
    logger.info("Google Ads API integration with the application completed")
