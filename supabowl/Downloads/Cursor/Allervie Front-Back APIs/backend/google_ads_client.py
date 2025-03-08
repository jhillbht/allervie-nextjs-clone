"""
Google Ads API Client Utility Module.

This module provides functions for interacting with the Google Ads API,
including client creation, query execution, and data formatting.
"""

import os
import logging
import traceback
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable debug logging for the Google Ads client library
googleads_logger = logging.getLogger('google.ads.googleads')
googleads_logger.setLevel(logging.DEBUG)

def get_google_ads_client():
    """
    Creates and returns a Google Ads API client.
    
    Loads the client configuration from the google-ads.yaml file
    in various possible locations.
    
    Returns:
        GoogleAdsClient: Configured client for Google Ads API
        None: If client creation fails
    """
    try:
        # Try to import the environment setting
        try:
            from config import ENVIRONMENT
            logger.info(f"Current environment: {ENVIRONMENT}")
        except ImportError:
            ENVIRONMENT = "production"
            logger.info(f"Defaulting to environment: {ENVIRONMENT}")
        
        # Try different locations for the google-ads.yaml file
        possible_paths = [
            Path(__file__).parent.parent / "credentials" / "google-ads.yaml",  # Parent credentials directory
            Path(__file__).parent / "google-ads.yaml",  # Current directory
            Path.cwd() / "credentials" / "google-ads.yaml",  # Working directory credentials
            Path.cwd() / "google-ads.yaml",  # Working directory
        ]
        
        yaml_path = None
        # Check each path and use the first one that exists
        for path in possible_paths:
            if path.exists():
                yaml_path = str(path)
                logger.info(f"Found google-ads.yaml at: {yaml_path}")
                break
        
        if not yaml_path:
            logger.error("google-ads.yaml not found in any of the expected locations")
            return None
        
        # Explicitly check and print YAML file contents (without sensitive info)
        try:
            import yaml
            with open(yaml_path, 'r') as yaml_file:
                config = yaml.safe_load(yaml_file)
                # Log some non-sensitive info to verify file is loaded correctly
                logger.info(f"YAML config contains login_customer_id: {config.get('login_customer_id', 'Not Found')}")
                logger.info(f"YAML config contains api_version: {config.get('api_version', 'Not Found')}")
                logger.info(f"YAML config contains use_proto_plus: {config.get('use_proto_plus', 'Not Found')}")
                
                # Verify required fields
                required_fields = ['client_id', 'client_secret', 'developer_token', 'login_customer_id', 'refresh_token']
                missing_fields = [field for field in required_fields if not config.get(field)]
                if missing_fields:
                    error_msg = f"Missing required fields in google-ads.yaml: {missing_fields}"
                    logger.error(error_msg)
                    
                    if ENVIRONMENT == "production":
                        raise ValueError(error_msg)
                    return None
                    
        except Exception as yaml_error:
            logger.error(f"Error reading YAML file: {yaml_error}")
            if ENVIRONMENT == "production":
                raise
            return None
        
        # Load the client with the API version from the YAML file, defaulting to v14
        api_version = config.get('api_version', 'v14') if config else 'v14'
        
        try:
            client = GoogleAdsClient.load_from_storage(yaml_path, version=api_version)
            
            # Verify the client was created correctly
            if client is None:
                error_msg = "GoogleAdsClient.load_from_storage returned None"
                logger.error(error_msg)
                if ENVIRONMENT == "production":
                    raise ValueError(error_msg)
                return None
                
            logger.info(f"Successfully loaded Google Ads client with API version {api_version}")
            logger.info(f"Client type: {type(client).__name__}")
            
            # Test if the client has the necessary methods
            if not hasattr(client, 'get_service'):
                error_msg = "Client missing required 'get_service' method"
                logger.error(error_msg)
                if ENVIRONMENT == "production":
                    raise ValueError(error_msg)
                return None
                
            # Try to get a service to verify the client works
            try:
                service = client.get_service('GoogleAdsService')
                logger.info(f"Successfully got GoogleAdsService: {type(service).__name__}")
                
                # Test the service with a simple query
                test_query = """
                    SELECT customer.id
                    FROM customer
                    LIMIT 1
                """
                try:
                    service.search(
                        customer_id=config['login_customer_id'],
                        query=test_query
                    )
                    logger.info("Successfully executed test query")
                except Exception as query_error:
                    logger.error(f"Test query failed: {query_error}")
                    if ENVIRONMENT == "production":
                        raise
                    return None
                    
            except Exception as service_error:
                logger.error(f"Error getting GoogleAdsService: {service_error}")
                if ENVIRONMENT == "production":
                    raise
                return None
                
            return client
        except Exception as e:
            logger.error(f"Failed to create client with API version {api_version}: {e}")
            
            # Fall back to try alternative versions
            fallback_versions = ['v19', 'v18', 'v17']
            for version in fallback_versions:
                try:
                    logger.info(f"Trying fallback to API version {version}")
                    client = GoogleAdsClient.load_from_storage(yaml_path, version=version)
                    if client and hasattr(client, 'get_service'):
                        logger.info(f"Fallback to {version} successful!")
                        return client
                except Exception:
                    continue  # Try next version
                    
            logger.error("All fallback version attempts failed")
            if ENVIRONMENT == "production":
                raise ValueError("Failed to create Google Ads client with any API version")
            return None
    except Exception as e:
        logger.error(f"Error getting Google Ads client: {e}")
        logger.error(traceback.format_exc())
        if ENVIRONMENT == "production":
            raise
        return None

def get_ads_performance(start_date=None, end_date=None, previous_period=False):
    """
    Fetches performance metrics from Google Ads API for the specified date range.
    
    This function retrieves key metrics from the Google Ads API, including impressions,
    clicks, conversions, and costs. It calculates derived metrics like CTR, conversion
    rate, and cost per conversion. When previous_period is True, it also fetches data
    for the previous time period of the same length and calculates percentage changes.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
            Defaults to 30 days ago.
        end_date (str, optional): End date in YYYY-MM-DD format.
            Defaults to yesterday.
        previous_period (bool, optional): If True, fetch data for the previous
            period of the same length and calculate percentage changes. 
            Defaults to False.
    
    Returns:
        dict: Performance metrics for the specified period with values and percentage changes.
              Each metric includes a 'value' and 'change' field.
        None: If the request fails
    """
    # Get Google Ads client
    client = get_google_ads_client()
    if not client:
        logger.error("Failed to create Google Ads client")
        return None
    
    # Set default date range if not provided
    today = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    
    if not end_date:
        # Default to yesterday
        end_date_obj = today - timedelta(days=1)
        end_date = end_date_obj.strftime('%Y-%m-%d')
    else:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        except ValueError:
            logger.error(f"Invalid end date format: {end_date}. Must be YYYY-MM-DD")
            return None
    
    if not start_date:
        # Default to 30 days ago instead of 7 days ago to get a better trend view
        start_date_obj = today - timedelta(days=30)
        start_date = start_date_obj.strftime('%Y-%m-%d')
    else:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        except ValueError:
            logger.error(f"Invalid start date format: {start_date}. Must be YYYY-MM-DD")
            return None
    
    logger.info(f"Fetching Google Ads performance data for period: {start_date} to {end_date}")
    
    # Calculate previous period date range if requested
    if previous_period:
        period_length = (end_date_obj - start_date_obj).days
        prev_end_date_obj = start_date_obj - timedelta(days=1)
        prev_start_date_obj = prev_end_date_obj - timedelta(days=period_length)
        prev_start_date = prev_start_date_obj.strftime('%Y-%m-%d')
        prev_end_date = prev_end_date_obj.strftime('%Y-%m-%d')
        logger.info(f"Will also fetch previous period: {prev_start_date} to {prev_end_date}")
    
    try:
        # MCC accounts can't query metrics directly - must use a client account
        # Get the manager account ID for authentication
        manager_id = client.login_customer_id
        if not manager_id:
            logger.error("No manager ID found in client configuration")
            return None
        
        # Get the client account ID from config, falling back to manager ID if not found
        try:
            from config import CLIENT_CUSTOMER_ID
            customer_id = CLIENT_CUSTOMER_ID
            logger.info(f"Using client account ID from config: {customer_id}")
        except ImportError:
            logger.warning("CLIENT_CUSTOMER_ID not found in config, using first non-manager account")
            # If no client ID is configured, try to find a non-manager account
            try:
                customer_service = client.get_service('CustomerService')
                response = customer_service.list_accessible_customers()
                
                # Find first non-manager account (any account other than the login account)
                for resource_name in response.resource_names:
                    account_id = resource_name.split('/')[-1]
                    if account_id != manager_id:
                        customer_id = account_id
                        logger.info(f"Using first non-manager account found: {customer_id}")
                        break
                else:
                    logger.error("No non-manager accounts found")
                    return None
            except Exception as e:
                logger.error(f"Error finding client accounts: {e}")
                return None
        
        # Create Google Ads query with enhanced metrics for v19 API
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
        
        # Get the service and execute query
        ga_service = client.get_service("GoogleAdsService")
        if not ga_service:
            logger.error("Failed to get GoogleAdsService")
            return None
            
        logger.info("Successfully got GoogleAdsService")
        
        # Execute the query with proper error handling
        try:
            search_response = ga_service.search(
                customer_id=customer_id,  # Use the client account ID, not the manager ID
                query=query
            )
            logger.info("Successfully executed search query")
        except GoogleAdsException as google_ads_error:
            logger.error(f"Google Ads API error: {google_ads_error}")
            return None
        except Exception as e:
            logger.error(f"Error executing search query: {e}")
            return None
        
        # Process the response
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_cost_micros = 0
        total_weighted_ctr = 0
        total_weighted_conv_rate = 0
        total_weighted_cost_per_conv = 0
        
        # Process each row in the response
        for row in search_response:
            metrics = row.metrics
            total_impressions += metrics.impressions
            total_clicks += metrics.clicks
            total_conversions += metrics.conversions
            total_cost_micros += metrics.cost_micros
            
            # Calculate weighted rate metrics
            if metrics.impressions > 0:
                total_weighted_ctr += metrics.ctr * metrics.impressions
            if metrics.clicks > 0:
                total_weighted_conv_rate += metrics.all_conversions_from_interactions_rate * metrics.clicks
            if metrics.conversions > 0:
                total_weighted_cost_per_conv += metrics.cost_per_conversion * metrics.conversions
        
        # Calculate averages and format metrics
        avg_ctr = (total_weighted_ctr / total_impressions) if total_impressions > 0 else 0
        avg_conv_rate = (total_weighted_conv_rate / total_clicks) if total_clicks > 0 else 0
        avg_cost_per_conv = (total_weighted_cost_per_conv / total_conversions) if total_conversions > 0 else 0
        total_cost = total_cost_micros / 1_000_000  # Convert micros to actual currency
        
        # Format the response with only real data from the API
        # Only include metrics that we actually got from the API
        current_period_data = {}
        
        # Add data points only if we have real data
        if total_impressions is not None:
            current_period_data["impressions"] = total_impressions
        
        if total_clicks is not None:
            current_period_data["clicks"] = total_clicks
            
        if total_conversions is not None:
            current_period_data["conversions"] = total_conversions
            
        if total_cost_micros is not None:
            current_period_data["cost"] = total_cost
            
        if total_impressions > 0 and avg_ctr is not None:
            current_period_data["clickThroughRate"] = avg_ctr
        
        if total_clicks > 0 and avg_conv_rate is not None:
            current_period_data["conversionRate"] = avg_conv_rate
            
        if total_conversions > 0 and avg_cost_per_conv is not None:
            current_period_data["costPerConversion"] = avg_cost_per_conv
        
        # If previous period data is requested, fetch it
        if previous_period:
            prev_query = query.replace(start_date, prev_start_date).replace(end_date, prev_end_date)
            try:
                prev_response = ga_service.search(
                    customer_id=customer_id,  # Use the client account ID, not the manager ID
                    query=prev_query
                )
                
                # Process previous period data similarly
                prev_metrics = {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "cost_micros": 0,
                    "weighted_ctr": 0,
                    "weighted_conv_rate": 0,
                    "weighted_cost_per_conv": 0
                }
                
                for row in prev_response:
                    metrics = row.metrics
                    prev_metrics["impressions"] += metrics.impressions
                    prev_metrics["clicks"] += metrics.clicks
                    prev_metrics["conversions"] += metrics.conversions
                    prev_metrics["cost_micros"] += metrics.cost_micros
                    
                    if metrics.impressions > 0:
                        prev_metrics["weighted_ctr"] += metrics.ctr * metrics.impressions
                    if metrics.clicks > 0:
                        prev_metrics["weighted_conv_rate"] += metrics.all_conversions_from_interactions_rate * metrics.clicks
                    if metrics.conversions > 0:
                        prev_metrics["weighted_cost_per_conv"] += metrics.cost_per_conversion * metrics.conversions
                
                # Calculate percentage changes
                def calc_change(current, previous):
                    if previous == 0:
                        return 0 if current == 0 else 100
                    return ((current - previous) / previous) * 100
                
                result = {
                    "impressions": {
                        "value": current_period_data["impressions"],
                        "change": calc_change(current_period_data["impressions"], prev_metrics["impressions"])
                    },
                    "clicks": {
                        "value": current_period_data["clicks"],
                        "change": calc_change(current_period_data["clicks"], prev_metrics["clicks"])
                    },
                    "conversions": {
                        "value": current_period_data["conversions"],
                        "change": calc_change(current_period_data["conversions"], prev_metrics["conversions"])
                    },
                    "cost": {
                        "value": current_period_data["cost"],
                        "change": calc_change(current_period_data["cost"], prev_metrics["cost_micros"] / 1_000_000)
                    },
                    "conversionRate": {
                        "value": current_period_data["conversionRate"],
                        "change": calc_change(current_period_data["conversionRate"], 
                                           (prev_metrics["weighted_conv_rate"] / prev_metrics["clicks"]) if prev_metrics["clicks"] > 0 else 0)
                    },
                    "clickThroughRate": {
                        "value": current_period_data["clickThroughRate"],
                        "change": calc_change(current_period_data["clickThroughRate"],
                                           (prev_metrics["weighted_ctr"] / prev_metrics["impressions"]) if prev_metrics["impressions"] > 0 else 0)
                    },
                    "costPerConversion": {
                        "value": current_period_data["costPerConversion"],
                        "change": calc_change(current_period_data["costPerConversion"],
                                           (prev_metrics["weighted_cost_per_conv"] / prev_metrics["conversions"]) if prev_metrics["conversions"] > 0 else 0)
                    }
                }
            except Exception as prev_error:
                logger.error(f"Error fetching previous period data: {prev_error}")
                # Return current period data without changes if previous period fails
                result = {metric: {"value": value, "change": 0} 
                         for metric, value in current_period_data.items()}
        else:
            # Return current period data without changes
            result = {metric: {"value": value, "change": 0} 
                     for metric, value in current_period_data.items()}
        
        logger.info("Successfully processed Google Ads performance data")
        return result
        
    except Exception as e:
        logger.error(f"Error processing Google Ads performance data: {e}")
        logger.error(traceback.format_exc())
        return None

def calculate_percentage_change(current, previous):
    """
    Calculate the percentage change between two values.
    
    Args:
        current (float): Current value
        previous (float): Previous value
    
    Returns:
        float: Percentage change
    """
    if previous == 0:
        return 0 if current == 0 else 100
    return ((current - previous) / previous) * 100
