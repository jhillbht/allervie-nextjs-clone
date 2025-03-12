"""
Google Ads client with Mock Data Fallback.

This module provides a function to get Google Ads performance data,
first trying real data from the Google Ads API, then falling back to mock data.
"""

import logging
import traceback
from datetime import datetime, timedelta
import random
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_ads_performance_with_fallback(start_date=None, end_date=None, previous_period=False):
    """
    Get Google Ads performance data with fallback to mock data.
    
    This function first attempts to get real data from the Google Ads API.
    If that fails, it returns an error response if mock data is disabled.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
        previous_period (bool, optional): If True, include previous period data.
    
    Returns:
        dict: Performance data, either real or mock.
    """
    # Import config
    from config import ENVIRONMENT, ALLOW_MOCK_DATA
    
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
                    if not ALLOW_MOCK_DATA:
                        logger.error("Mock data is disabled, returning error")
                        return {
                            "error": "Invalid data format",
                            "message": "Real data is missing required metrics or has invalid structure and mock data is disabled"
                        }
                    # Fall through to mock data if allowed
            else:
                logger.error("No real Google Ads data available")
                if not ALLOW_MOCK_DATA:
                    logger.error("Mock data is disabled, returning error")
                    return {
                        "error": "No data",
                        "message": "No real Google Ads data available and mock data is disabled"
                    }
                # Fall through to mock data if allowed
                
        except Exception as client_error:
            logger.error(f"Error getting real Google Ads performance data: {client_error}")
            if not ALLOW_MOCK_DATA:
                logger.error("Mock data is disabled, returning error")
                return {
                    "error": "API error",
                    "message": f"Error getting real Google Ads performance data: {client_error}"
                }
            # Fall through to mock data if allowed
                
    except ImportError as e:
        logger.error(f"Failed to import Google Ads client: {e}")
        if not ALLOW_MOCK_DATA:
            logger.error("Mock data is disabled, returning error")
            return {
                "error": "Import error",
                "message": f"Failed to import Google Ads client: {e}"
            }
        # Fall through to mock data if allowed
    except Exception as e:
        logger.error(f"Error in Google Ads client handling: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if not ALLOW_MOCK_DATA:
            logger.error("Mock data is disabled, returning error")
            return {
                "error": "System error",
                "message": f"Error in Google Ads client handling: {e}"
            }
        # Fall through to mock data if allowed
    
    # If we get here, the real data attempt failed
    # Check if we're allowed to use mock data
    if ALLOW_MOCK_DATA:
        logger.info("Using mock Google Ads performance data")
        
        # Generate mock data for development
        mock_data = {
            "impressions": {
                "value": random.randint(10000, 50000),
                "change": round(random.uniform(-20.0, 20.0), 1)
            },
            "clicks": {
                "value": random.randint(500, 5000),
                "change": round(random.uniform(-20.0, 20.0), 1)
            },
            "conversions": {
                "value": random.randint(50, 500),
                "change": round(random.uniform(-20.0, 20.0), 1)
            },
            "cost": {
                "value": round(random.uniform(1000, 10000), 2),
                "change": round(random.uniform(-20.0, 20.0), 1)
            },
            "conversionRate": {
                "value": round(random.uniform(1.0, 10.0), 2),
                "change": round(random.uniform(-20.0, 20.0), 1)
            },
            "clickThroughRate": {
                "value": round(random.uniform(1.0, 5.0), 2),
                "change": round(random.uniform(-20.0, 20.0), 1)
            },
            "costPerConversion": {
                "value": round(random.uniform(10.0, 50.0), 2),
                "change": round(random.uniform(-20.0, 20.0), 1)
            }
        }
        
        return mock_data
    else:
        logger.error("Mock data is disabled")
        return {
            "error": "No data available",
            "message": "Failed to retrieve Google Ads performance data and mock data is disabled",
            "impressions": {"value": 0, "change": 0},
            "clicks": {"value": 0, "change": 0},
            "conversions": {"value": 0, "change": 0},
            "cost": {"value": 0, "change": 0},
            "conversionRate": {"value": 0, "change": 0},
            "clickThroughRate": {"value": 0, "change": 0},
            "costPerConversion": {"value": 0, "change": 0}
        }

def get_campaign_performance_with_fallback(start_date=None, end_date=None):
    """
    Get Google Ads campaign performance data with fallback to mock data.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
    
    Returns:
        list: Campaign data, either real or mock.
    """
    # Import config
    from config import ENVIRONMENT, ALLOW_MOCK_DATA
    
    try:
        # Try to import the real campaign performance function
        from extended_google_ads_api import get_campaign_performance
        
        # Try to get real campaign data
        try:
            campaigns = get_campaign_performance(start_date=start_date, end_date=end_date)
            if campaigns:
                logger.info(f"Successfully retrieved {len(campaigns)} real campaigns")
                return campaigns
            else:
                logger.error("No campaign data returned from Google Ads API")
                if not ALLOW_MOCK_DATA:
                    logger.error("Mock data is disabled, returning None")
                    return {
                        "status": "error",
                        "message": "No campaign data available from Google Ads API and mock data is disabled",
                        "data": []
                    }
                # Fall through to mock data if allowed
        except Exception as e:
            logger.error(f"Error getting real campaign data: {str(e)}")
            if not ALLOW_MOCK_DATA:
                logger.error("Mock data is disabled, returning error")
                return {
                    "status": "error",
                    "message": f"Error retrieving campaign data: {str(e)}",
                    "data": []
                }
            # Fall through to mock data if allowed
            
    except ImportError:
        logger.error("Failed to import get_campaign_performance function")
        if not ALLOW_MOCK_DATA:
            logger.error("Mock data is disabled, returning error")
            return {
                "status": "error",
                "message": "Failed to import get_campaign_performance function and mock data is disabled",
                "data": []
            }
        # Fall through to mock data if allowed
    
    # If we get here, the real data attempt failed
    # Check if we're allowed to use mock data
    if ALLOW_MOCK_DATA:
        logger.info("Using mock campaign performance data")
        
        # Generate diverse mock campaign data with real-world campaign name formats
        campaign_names = [
            "AllerVie Health - Brand Awareness",
            "TX-Dallas Allergy Clinics PMax",
            "FL-Miami Asthma Treatment - Display",
            "GA-Atlanta Immunotherapy - Search",
            "NC-Charlotte Allergy Testing",
            "Brand - AllerVie Treatments",
            "Non-Brand - Allergy Specialists",
            "Seasonal - Spring Allergies 2025",
            "Remarketing - Website Visitors",
            "AllerVie Doctors Near Me - Search",
            "Food Allergy Testing - Exact Match",
            "Pediatric Allergy - Broad Match",
            "VA-Richmond Allergy Relief",
            "TN-Nashville Sinus Treatment",
            "LA-New Orleans Asthma Specialists"
        ]
        
        statuses = ["ENABLED", "ENABLED", "PAUSED", "ENABLED", "ENABLED", 
                   "ENABLED", "PAUSED", "ENABLED", "ENABLED", "ENABLED",
                   "PAUSED", "ENABLED", "ENABLED", "PAUSED", "ENABLED"]
        
        # Generate random performance data for each campaign
        mock_campaigns = []
        for i, name in enumerate(campaign_names):
            # Use mod operator to handle cases if we have more campaign names than statuses
            status_index = i % len(statuses)
            impressions = random.randint(1000, 100000)
            clicks = random.randint(10, min(impressions, 5000))
            conversions = random.randint(0, min(clicks, 500))
            cost_dollars = round(random.uniform(10, 5000), 2)
            
            campaign = {
                "id": str(1000000 + i),
                "name": name,
                "status": statuses[status_index],
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "cost": cost_dollars,  # Store as a numeric value, not a string with $ prefix
                "ctr": round((clicks / impressions * 100) if impressions > 0 else 0, 2),
                "conversionRate": round((conversions / clicks * 100) if clicks > 0 else 0, 2)
            }
            mock_campaigns.append(campaign)
        
        # Add a structured response
        response = {
            "status": "success",
            "message": "Data retrieved from mock data",
            "data": mock_campaigns
        }
        
        return response
    else:
        logger.error("Mock campaign data is disabled")
        return {
            "status": "error",
            "message": "Failed to retrieve real campaign data and mock data is disabled",
            "data": []
        }