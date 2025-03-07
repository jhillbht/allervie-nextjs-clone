"""
Google Ads client with fallback to mock data.

This module provides a function to get Google Ads performance data,
first attempting to get real data from the Google Ads API,
but falling back to mock data if the API call fails.
"""

import logging
import random
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_mock_ads_performance(start_date=None, end_date=None, previous_period=False):
    """
    Generate mock Google Ads performance data.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
        previous_period (bool, optional): If True, include previous period data.
    
    Returns:
        dict: Mock performance data with realistic values.
    """
    logger.info(f"Generating mock Google Ads performance data for period: {start_date or 'default'} to {end_date or 'default'}")
    
    try:
        # Generate realistic metrics with some randomness
        impressions = random.randint(75000, 250000)
        clicks = int(impressions * random.uniform(0.01, 0.05))  # 1-5% CTR
        conversions = int(clicks * random.uniform(0.01, 0.1))  # 1-10% conversion rate
        cost = round(clicks * random.uniform(0.5, 3.0), 2)  # $0.50-$3.00 CPC
        
        # Calculate rate metrics
        ctr = round((clicks / impressions * 100) if impressions > 0 else 0, 2)
        conv_rate = round((conversions / clicks * 100) if clicks > 0 else 0, 2)
        cost_per_conv = round((cost / conversions) if conversions > 0 else 0, 2)
        
        # Change percentages - between -20% and +50% to show growth trends
        if previous_period:
            changes = {
                metric: round(random.uniform(-20, 50), 1)
                for metric in ["impressions", "clicks", "conversions", "cost", "ctr", "conv_rate", "cost_per_conv"]
            }
        else:
            changes = {
                metric: 0
                for metric in ["impressions", "clicks", "conversions", "cost", "ctr", "conv_rate", "cost_per_conv"]
            }
        
        # Format the response in the expected structure
        result = {
            "impressions": {
                "value": impressions,
                "change": changes["impressions"]
            },
            "clicks": {
                "value": clicks,
                "change": changes["clicks"]
            },
            "conversions": {
                "value": conversions,
                "change": changes["conversions"]
            },
            "cost": {
                "value": cost,
                "change": changes["cost"]
            },
            "conversionRate": {
                "value": conv_rate,
                "change": changes["conv_rate"]
            },
            "clickThroughRate": {
                "value": ctr,
                "change": changes["ctr"]
            },
            "costPerConversion": {
                "value": cost_per_conv,
                "change": changes["cost_per_conv"]
            }
        }
        
        logger.info("Successfully generated mock Google Ads performance data")
        return result
        
    except Exception as e:
        logger.error(f"Error generating mock Google Ads performance data: {e}")
        logger.error(traceback.format_exc())
        
        # Return a safe fallback with zeros
        return {
            metric: {"value": 0, "change": 0}
            for metric in [
                "impressions", "clicks", "conversions", "cost",
                "conversionRate", "clickThroughRate", "costPerConversion"
            ]
        }

def get_ads_performance_with_fallback(start_date=None, end_date=None, previous_period=False):
    """
    Get Google Ads performance data, with fallback to mock data if allowed.
    
    This function first tries to get real data from the Google Ads API.
    If that fails, it falls back to generating mock data only if ALLOW_MOCK_DATA is True.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
        previous_period (bool, optional): If True, include previous period data.
    
    Returns:
        dict: Performance data, either real or mock.
        None: If real data fails and mock data is not allowed.
    """
    # Import config
    from config import ALLOW_MOCK_DATA, ENVIRONMENT
    
    try:
        # Try to import the real Google Ads client - always attempt this first
        from google_ads_client import get_ads_performance
        
        # Try to get real data first
        logger.info(f"Attempting to get real Google Ads performance data in {ENVIRONMENT} environment")
        
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
                    if not ALLOW_MOCK_DATA:
                        logger.error("Mock data is disabled, returning empty dataset")
                        return None
                    logger.info("Falling back to mock Google Ads performance data")
            else:
                logger.info("No real Google Ads data available")
                if not ALLOW_MOCK_DATA:
                    logger.error("Mock data is disabled, returning empty dataset")
                    return None
                logger.info("Falling back to mock data")
                
        except Exception as client_error:
            logger.error(f"Error getting real Google Ads performance data: {client_error}")
            if not ALLOW_MOCK_DATA:
                logger.error("Mock data is disabled, returning empty dataset")
                return None
            logger.info("Falling back to mock Google Ads performance data due to error")
                
    except ImportError as e:
        logger.error(f"Failed to import Google Ads client: {e}")
        if not ALLOW_MOCK_DATA:
            logger.error("Mock data is disabled, returning empty dataset")
            return None
    except Exception as e:
        logger.error(f"Error in Google Ads client handling: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if not ALLOW_MOCK_DATA:
            logger.error("Mock data is disabled, returning empty dataset")
            return None
    
    # If we get here, either the import failed or getting real data failed
    # and ALLOW_MOCK_DATA must be True
    logger.info("Using mock Google Ads performance data")
    return get_mock_ads_performance(start_date, end_date, previous_period)
