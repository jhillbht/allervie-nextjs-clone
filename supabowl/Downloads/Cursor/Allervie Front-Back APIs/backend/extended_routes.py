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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import from app
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Try to import configuration flags from config.py
try:
    from config import USE_REAL_ADS_CLIENT, ENVIRONMENT
    logger.info(f"Successfully imported configuration settings:")
    logger.info(f"USE_REAL_ADS_CLIENT: {USE_REAL_ADS_CLIENT}")
    logger.info(f"ENVIRONMENT: {ENVIRONMENT}")
except ImportError as e:
    logger.warning(f"Could not import config settings: {e}")
    USE_REAL_ADS_CLIENT = True
    ENVIRONMENT = "production"

try:
    from extended_google_ads_api import (
        get_google_ads_client,
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
    
    # Use only real data
    try:
        # Create a Google Ads client
        client = get_google_ads_client()
        if client:
            logger.info(f"Successfully created Google Ads client")
            # Get campaign performance data
            real_data = get_campaign_performance(client)
            if real_data:
                logger.info(f"Successfully retrieved {len(real_data)} campaigns")
                return jsonify(real_data)
            else:
                logger.error("No campaign data returned from Google Ads API")
                return jsonify({
                    "error": "No data available",
                    "message": "No campaign data returned from Google Ads API",
                    "environment": ENVIRONMENT
                }), 404
        else:
            logger.error("Failed to create Google Ads client")
            return jsonify({
                "error": "API connection failed",
                "message": "Failed to create Google Ads client",
                "environment": ENVIRONMENT
            }), 500
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
    
    logger.info(f"Received request for ad groups")
    
    # Use only real data
    try:
        # Create a Google Ads client
        client = get_google_ads_client()
        if client:
            logger.info(f"Successfully created Google Ads client")
            # Get ad group performance data
            real_data = get_ad_group_performance(client)
            if real_data:
                logger.info(f"Successfully retrieved {len(real_data)} ad groups")
                return jsonify(real_data)
            else:
                logger.error("No ad group data returned from Google Ads API")
                return jsonify({
                    "error": "No data available",
                    "message": "No ad group data returned from Google Ads API",
                    "environment": ENVIRONMENT
                }), 404
        else:
            logger.error("Failed to create Google Ads client")
            return jsonify({
                "error": "API connection failed",
                "message": "Failed to create Google Ads client",
                "environment": ENVIRONMENT
            }), 500
    except Exception as e:
        logger.error(f"Error getting ad group data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "API error",
            "message": f"Error retrieving ad group data: {str(e)}",
            "environment": ENVIRONMENT
        }), 500

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
        # Create a Google Ads client
        client = get_google_ads_client()
        if client and get_search_term_performance:
            search_terms_data = get_search_term_performance(start_date, end_date, campaign_id)
            if search_terms_data:
                logger.info(f"Successfully retrieved search terms data")
                return jsonify(search_terms_data)
            else:
                logger.error("No search terms data returned from Google Ads API")
                return jsonify({
                    "error": "No data available",
                    "message": "No search terms data returned from Google Ads API",
                    "environment": ENVIRONMENT
                }), 404
        else:
            logger.error("Failed to create Google Ads client or get_search_term_performance function")
            return jsonify({
                "error": "API connection failed",
                "message": "Failed to create Google Ads client or get search term performance function",
                "environment": ENVIRONMENT
            }), 500
    except Exception as e:
        logger.error(f"Error fetching search term data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "API error",
            "message": f"Error retrieving search term data: {str(e)}",
            "environment": ENVIRONMENT
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
        if get_search_term_performance:
            real_data = get_search_term_performance(start_date=start_date, end_date=end_date, ad_group_id=ad_group_id)
            if real_data:
                logger.info(f"Successfully retrieved keyword data")
                return jsonify(real_data)
            else:
                logger.error("No keyword data returned from Google Ads API")
                return jsonify({
                    "error": "No data available",
                    "message": "No keyword data returned from Google Ads API",
                    "environment": ENVIRONMENT
                }), 404
        else:
            logger.error("Failed to create Google Ads client or get_search_term_performance function")
            return jsonify({
                "error": "API connection failed",
                "message": "Failed to create Google Ads client or get keyword performance function",
                "environment": ENVIRONMENT
            }), 500
    except Exception as e:
        logger.error(f"Error fetching keyword data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "API error",
            "message": f"Error retrieving keyword data: {str(e)}",
            "environment": ENVIRONMENT
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
        if get_search_term_performance:
            real_data = get_search_term_performance(start_date=start_date, end_date=end_date, ad_group_id=ad_group_id)
            if real_data:
                logger.info(f"Successfully retrieved ad performance data")
                return jsonify(real_data)
            else:
                logger.error("No ad data returned from Google Ads API")
                return jsonify({
                    "error": "No data available",
                    "message": "No ad data returned from Google Ads API",
                    "environment": ENVIRONMENT
                }), 404
        else:
            logger.error("Failed to create Google Ads client or get ad performance function")
            return jsonify({
                "error": "API connection failed",
                "message": "Failed to create Google Ads client or get ad performance function",
                "environment": ENVIRONMENT
            }), 500
    except Exception as e:
        logger.error(f"Error fetching ad performance data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "API error",
            "message": f"Error retrieving ad performance data: {str(e)}",
            "environment": ENVIRONMENT
        }), 500