"""
Extended API Routes for Google Ads

This module provides additional API routes for the Google Ads API,
including endpoints for campaign data, ad group data, keyword data, and more.
"""

from flask import Blueprint, jsonify, request, session
import logging
import sys
from datetime import datetime
import traceback
import os
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import from app
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Try to import configuration flags from config.py
try:
    from config import USE_REAL_ADS_CLIENT, ENVIRONMENT, ALLOW_MOCK_DATA
    logger.info(f"Successfully imported configuration settings:")
    logger.info(f"USE_REAL_ADS_CLIENT: {USE_REAL_ADS_CLIENT}")
    logger.info(f"ENVIRONMENT: {ENVIRONMENT}")
except ImportError as e:
    logger.warning(f"Could not import config settings: {e}")
    USE_REAL_ADS_CLIENT = True
    ENVIRONMENT = "production"
    ALLOW_MOCK_DATA = False

try:
    from extended_google_ads_api import (
        get_campaign_performance,
        get_ad_group_performance,
        get_search_term_performance
    )
    logger.info("Successfully imported Google Ads API functions")
except ImportError:
    logger.error("Failed to import Google Ads API functions")
    traceback.print_exc()
    get_campaign_performance = None
    get_ad_group_performance = None
    get_search_term_performance = None

# Create a blueprint for the Google Ads API routes
extended_bp = Blueprint('extended_bp', __name__)

# List of available Google Ads API endpoints
AVAILABLE_ENDPOINTS = [
    {"name": "Campaigns", "endpoint": "/api/google-ads/campaigns", "description": "Campaign performance data"},
    {"name": "Ad Groups", "endpoint": "/api/google-ads/ad_groups", "description": "Ad group performance data"},
    {"name": "Keywords", "endpoint": "/api/google-ads/keywords", "description": "Keyword performance data"},
    {"name": "Search Terms", "endpoint": "/api/google-ads/search_terms", "description": "Search term performance data"},
    {"name": "Ads", "endpoint": "/api/google-ads/ads", "description": "Ad performance data"},
    {"name": "Performance", "endpoint": "/api/google-ads/performance", "description": "Overall performance metrics"}
]

@extended_bp.route('/available_endpoints', methods=['GET'])
def get_available_endpoints():
    """Get list of available Google Ads API endpoints"""
    # Verify authentication
    auth_header = request.headers.get('Authorization', '')
    
    # If no authorization header or invalid token format, require authentication
    if not auth_header.startswith('Bearer ') and 'user_id' not in session:
        logger.warning("Unauthorized access attempt to available_endpoints")
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
        
    return jsonify(AVAILABLE_ENDPOINTS)

@extended_bp.route('/campaigns', methods=['GET'])
def get_campaigns():
    """
    Get campaign performance data
    """
    # Verify authentication
    auth_header = request.headers.get('Authorization', '')
    
    # If no authorization header or invalid token format, require authentication
    if not auth_header.startswith('Bearer ') and 'user_id' not in session:
        logger.warning("Unauthorized access attempt to campaigns endpoint")
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    
    # Get request parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    logger.info(f"Received request for campaigns")
    
    try:
        # Import the fallback function
        from google_ads_fallback import get_campaign_performance_with_fallback
        
        # Get campaign data with fallback to mock data
        response = get_campaign_performance_with_fallback(start_date, end_date)
        
        if response:
            # Check if response is already a json structure with status and data
            if isinstance(response, dict) and 'status' in response and 'data' in response:
                return jsonify(response)
            # Check if it's an error response
            elif isinstance(response, dict) and 'error' in response:
                logger.error(f"Error in campaign data: {response.get('message', 'Unknown error')}")
                return jsonify(response), 400
            # If it's just a plain array
            elif isinstance(response, list):
                # Return as data
                return jsonify({
                    "status": "success",
                    "message": "Campaign data retrieved",
                    "data": response
                })
            # If it's a dict without the expected structure
            else:
                # Return as data
                return jsonify({
                    "status": "success",
                    "message": "Campaign data retrieved",
                    "data": response
                })
        else:
            logger.error("No campaign data returned from API or mock data")
            return jsonify({
                "status": "error",
                "message": "No campaign data available",
                "data": [],
                "environment": ENVIRONMENT
            }), 404
    except Exception as e:
        logger.error(f"Error getting campaign data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "API error",
            "message": f"Error retrieving campaign data: {str(e)}",
            "environment": ENVIRONMENT
        }), 500

@extended_bp.route('/ad_groups', methods=['GET'])
def get_ad_groups():
    """
    Get ad group performance data
    """
    # Verify authentication
    auth_header = request.headers.get('Authorization', '')
    
    # If no authorization header or invalid token format, require authentication
    if not auth_header.startswith('Bearer ') and 'user_id' not in session:
        logger.warning("Unauthorized access attempt to ad_groups endpoint")
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    
    # Get request parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    campaign_id = request.args.get('campaign_id')
    
    logger.info(f"Received request for ad groups (campaign_id: {campaign_id})")
    
    # Try to get real ad group data
    try:
        # Get real ad group data
        ad_groups = get_ad_group_performance(start_date=start_date, end_date=end_date, campaign_id=campaign_id)
        
        if ad_groups:
            logger.info(f"Successfully retrieved {len(ad_groups)} real ad groups")
            
            # Return in a consistent format
            return jsonify({
                "status": "success",
                "message": "Ad group data retrieved from Google Ads API",
                "data": ad_groups
            })
        else:
            logger.error("No ad group data returned from Google Ads API")
            
            # If mock data is not allowed, return an error
            if not ALLOW_MOCK_DATA:
                return jsonify({
                    "status": "error",
                    "message": "No ad group data available from Google Ads API and mock data is disabled",
                    "data": []
                }), 404
            
    except Exception as e:
        logger.error(f"Error getting real ad group data: {e}")
        logger.error(traceback.format_exc())
        
        # Check if mock data is allowed
        if not ALLOW_MOCK_DATA:
            return jsonify({
                "status": "error", 
                "message": f"Error retrieving ad group data: {str(e)}",
                "data": []
            }), 500
            
    # Only get here if real data failed and mock data is allowed
    logger.warning("Using mock ad group data since real API request failed")
    
    # Generate mock data with more realistic ad group names
    ad_group_names = [
        "Branded - AllerVie Health Exact", 
        "AllerVie Locations - Phrase Match",
        "Allergy Symptoms - Broad Match",
        "Allergy Treatment - Phrase Match", 
        "Food Allergy Testing - Exact",
        "Allergy Doctors - Broad",
        "Asthma Treatment - Exact", 
        "Immunotherapy - Broad",
        "Sinus Treatment - Phrase",
        "Pediatric Allergies - Exact"
    ]
    
    statuses = ["ENABLED", "ENABLED", "PAUSED", "ENABLED", "ENABLED", 
               "PAUSED", "ENABLED", "ENABLED", "ENABLED", "PAUSED"]
    
    # Generate random performance data for each ad group
    mock_ad_groups = []
    for i, name in enumerate(ad_group_names):  # Use all ad group names
        impressions = random.randint(500, 50000)
        clicks = random.randint(5, min(impressions, 2000))
        conversions = random.randint(0, min(clicks, 100))
        cost_dollars = round(random.uniform(5, 500), 2)
        
        ad_group = {
            "id": str(2000000 + i),
            "campaign_id": campaign_id,
            "name": name,
            "status": statuses[i % len(statuses)],  # Use modulo in case we have more ad groups than statuses
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "cost": cost_dollars,  # Store as a numeric value, not a string with $ prefix
            "ctr": round((clicks / impressions * 100) if impressions > 0 else 0, 2),
            "conversionRate": round((conversions / clicks * 100) if clicks > 0 else 0, 2)
        }
        mock_ad_groups.append(ad_group)
    
    logger.info(f"Successfully generated {len(mock_ad_groups)} mock ad groups")
    
    # Return the mock data
    return jsonify({
        "status": "success",
        "message": "Ad group data retrieved (mock data)",
        "data": mock_ad_groups
    })

@extended_bp.route('/search_terms', methods=['GET'])
def get_search_terms():
    """
    Get search terms performance data
    """
    # Verify authentication
    auth_header = request.headers.get('Authorization', '')
    
    # If no authorization header or invalid token format, require authentication
    if not auth_header.startswith('Bearer ') and 'user_id' not in session:
        logger.warning("Unauthorized access attempt to search_terms endpoint")
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    
    # Get date range and campaign ID from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    campaign_id = request.args.get('campaign_id')
    
    logger.info(f"Received request for search terms")
    
    # Use only real data
    try:
        # Get search terms data directly
        search_terms_data = get_search_term_performance(start_date=start_date, end_date=end_date, ad_group_id=campaign_id)
        
        if search_terms_data:
            logger.info(f"Successfully retrieved search terms data")
            return jsonify({
                "status": "success",
                "message": "Search terms data retrieved",
                "data": search_terms_data
            })
        else:
            logger.error("No search terms data returned from Google Ads API")
            return jsonify({
                "status": "error",
                "message": "No search terms data returned from Google Ads API",
                "data": []
            }), 404
    except Exception as e:
        logger.error(f"Error fetching search term data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"Error retrieving search term data: {str(e)}",
            "data": []
        }), 500

@extended_bp.route('/keywords', methods=['GET'])
def get_keywords():
    """
    Get keyword performance data
    """
    # Verify authentication
    auth_header = request.headers.get('Authorization', '')
    
    # If no authorization header or invalid token format, require authentication
    if not auth_header.startswith('Bearer ') and 'user_id' not in session:
        logger.warning("Unauthorized access attempt to keywords endpoint")
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    
    # Get date range and ad group ID from request params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ad_group_id = request.args.get('ad_group_id')
    
    logger.info(f"Received request for keywords")
    
    # Use only real data
    try:
        # Call get_search_term_performance directly with parameters
        real_data = get_search_term_performance(start_date=start_date, end_date=end_date, ad_group_id=ad_group_id)
        if real_data:
            logger.info(f"Successfully retrieved keyword data")
            return jsonify({
                "status": "success",
                "message": "Keyword data retrieved",
                "data": real_data
            })
        else:
            logger.error("No keyword data returned from Google Ads API")
            return jsonify({
                "status": "error",
                "message": "No keyword data returned from Google Ads API",
                "data": []
            }), 404
    except Exception as e:
        logger.error(f"Error fetching keyword data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"Error retrieving keyword data: {str(e)}",
            "data": []
        }), 500

@extended_bp.route('/ads', methods=['GET'])
def get_ads():
    """
    Get ad performance data
    """
    # Verify authentication
    auth_header = request.headers.get('Authorization', '')
    
    # If no authorization header or invalid token format, require authentication
    if not auth_header.startswith('Bearer ') and 'user_id' not in session:
        logger.warning("Unauthorized access attempt to ads endpoint")
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    
    # Get date range and ad group ID from request params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ad_group_id = request.args.get('ad_group_id')
    
    logger.info(f"Received request for ads")
    
    # Use only real data
    try:
        # Call get_search_term_performance directly with parameters 
        real_data = get_search_term_performance(start_date=start_date, end_date=end_date, ad_group_id=ad_group_id)
        if real_data:
            logger.info(f"Successfully retrieved ad performance data")
            return jsonify({
                "status": "success",
                "message": "Ad performance data retrieved",
                "data": real_data
            })
        else:
            logger.error("No ad data returned from Google Ads API")
            return jsonify({
                "status": "error",
                "message": "No ad data returned from Google Ads API",
                "data": []
            }), 404
    except Exception as e:
        logger.error(f"Error fetching ad performance data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"Error retrieving ad performance data: {str(e)}",
            "data": []
        }), 500