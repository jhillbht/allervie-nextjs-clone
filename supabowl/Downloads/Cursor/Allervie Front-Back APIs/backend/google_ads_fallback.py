"""
Google Ads client - No Mock Data.

This module provides a function to get Google Ads performance data,
always using real data from the Google Ads API.
"""

import logging
import traceback
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_ads_performance_with_fallback(start_date=None, end_date=None, previous_period=False):
    """
    Get Google Ads performance data from the real API.
    
    This function always attempts to get real data from the Google Ads API.
    No mock data is ever returned.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
        previous_period (bool, optional): If True, include previous period data.
    
    Returns:
        dict: Performance data from the real API.
        None: If API call fails.
    """
    # Import config
    from config import ENVIRONMENT
    
    try:
        # Try to import the real Google Ads client
        from google_ads_client import get_ads_performance
        
        # Try to get real data
        logger.info(f"Getting real Google Ads performance data in {ENVIRONMENT} environment")
        
        try:
            real_data = get_ads_performance(start_date, end_date, previous_period)
            
            if real_data:
                # Validate the data structure
                required_metrics = [
                    "impressions", "clicks", "conversions", "cost",
                    "conversionRate", "clickThroughRate", "costPerConversion"
                ]
                
                # Check if all required metrics are present and have the correct structure
                is_valid = all(
                    metric in real_data and
                    isinstance(real_data[metric], dict) and
                    "value" in real_data[metric] and
                    "change" in real_data[metric]
                    for metric in required_metrics
                )
                
                if is_valid:
                    logger.info("Successfully retrieved and validated real Google Ads performance data")
                    return real_data
                else:
                    logger.error("Real data is missing required metrics or has invalid structure")
                    return None
            else:
                logger.error("No real Google Ads data available")
                return None
                
        except Exception as client_error:
            logger.error(f"Error getting real Google Ads performance data: {client_error}")
            return None
                
    except ImportError as e:
        logger.error(f"Failed to import Google Ads client: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in Google Ads client handling: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    
    # If we get here, there was an error
    return None

def get_campaign_performance_with_fallback(start_date=None, end_date=None):
    """
    Get Google Ads campaign performance data from the real API.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
    
    Returns:
        list: Campaign data from the real API.
        None: If API call fails.
    """
    try:
        # Try to import the real campaign performance function
        from extended_google_ads_api import get_campaign_performance
        
        # Try to get real campaign data
        try:
            campaigns = get_campaign_performance(start_date, end_date)
            if campaigns:
                logger.info(f"Successfully retrieved {len(campaigns)} real campaigns")
                return campaigns
            else:
                logger.error("No campaign data returned from Google Ads API")
                return None
        except Exception as e:
            logger.error(f"Error getting real campaign data: {str(e)}")
            return None
            
    except ImportError:
        logger.error("Failed to import get_campaign_performance function")
        return None
    
    # If we get here, there was an error
    return None