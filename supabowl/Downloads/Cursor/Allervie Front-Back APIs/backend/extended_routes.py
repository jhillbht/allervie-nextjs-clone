"""
Extended API Routes for Google Ads

This module provides additional API routes for the Google Ads API,
including endpoints for campaign data, ad group data, keyword data, and more.
"""

from flask import Blueprint, jsonify, request, session
import logging
import json
import random
import sys
from datetime import datetime, timedelta
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
    from config import USE_REAL_ADS_CLIENT, ALLOW_MOCK_DATA, ENVIRONMENT
    logger.info(f"Successfully imported configuration settings:")
    logger.info(f"USE_REAL_ADS_CLIENT: {USE_REAL_ADS_CLIENT}")
    logger.info(f"ALLOW_MOCK_DATA: {ALLOW_MOCK_DATA}")
    logger.info(f"ENVIRONMENT: {ENVIRONMENT}")
except ImportError as e:
    logger.warning(f"Could not import config settings: {e}")
    USE_REAL_ADS_CLIENT = True
    ALLOW_MOCK_DATA = False
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
    return jsonify(AVAILABLE_ENDPOINTS)

def create_na_response(entity_type):
    """Create a response with N/A values for when real data can't be fetched"""
    if entity_type == "campaign":
        return [{
            "campaign_id": "N/A",
            "campaign_name": "N/A",
            "status": "N/A",
            "budget": "N/A",
            "impressions": "N/A",
            "clicks": "N/A",
            "cost": "N/A",
            "conversions": "N/A",
            "ctr": "N/A",
            "cpc": "N/A",
            "conversion_rate": "N/A",
            "cost_per_conversion": "N/A"
        }]
    elif entity_type == "ad_group":
        return [{
            "ad_group_id": "N/A",
            "ad_group_name": "N/A",
            "campaign_id": "N/A",
            "status": "N/A",
            "impressions": "N/A",
            "clicks": "N/A",
            "cost": "N/A",
            "conversions": "N/A",
            "ctr": "N/A",
            "cpc": "N/A",
            "conversion_rate": "N/A",
            "cost_per_conversion": "N/A"
        }]
    elif entity_type == "keyword":
        return [{
            "keyword_id": "N/A",
            "keyword_text": "N/A",
            "match_type": "N/A",
            "ad_group_id": "N/A",
            "status": "N/A",
            "quality_score": "N/A",
            "impressions": "N/A",
            "clicks": "N/A",
            "cost": "N/A",
            "conversions": "N/A",
            "ctr": "N/A",
            "cpc": "N/A",
            "conversion_rate": "N/A",
            "cost_per_conversion": "N/A"
        }]
    elif entity_type == "search_term":
        return [{
            "search_term": "N/A",
            "impressions": "N/A",
            "clicks": "N/A",
            "cost": "N/A",
            "conversions": "N/A",
            "ctr": "N/A",
            "cpc": "N/A",
            "conversion_rate": "N/A",
            "cost_per_conversion": "N/A"
        }]
    elif entity_type == "ad":
        return [{
            "ad_id": "N/A",
            "ad_type": "N/A",
            "ad_group_id": "N/A",
            "headline": "N/A",
            "description": "N/A",
            "final_url": "N/A",
            "status": "N/A",
            "impressions": "N/A",
            "clicks": "N/A",
            "cost": "N/A",
            "conversions": "N/A",
            "ctr": "N/A",
            "cpc": "N/A",
            "conversion_rate": "N/A",
            "cost_per_conversion": "N/A"
        }]
    return [{"error": "Unknown entity type"}]

@extended_bp.route('/campaigns', methods=['GET'])
def get_campaigns():
    """
    Get campaign performance data
    """
    # Get request parameters
    token = request.args.get('token')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    logger.info(f"Received request for campaigns with token: {token}")
    logger.info(f"USE_REAL_ADS_CLIENT is set to: {USE_REAL_ADS_CLIENT}")
    
    # Check if we should use real data
    use_real = USE_REAL_ADS_CLIENT or session.get('use_real_ads_client', False)
    logger.info(f"Using real data: {use_real}")
    
    # Try to get real data first
    if use_real and get_campaign_performance and get_google_ads_client:
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
                    logger.warning("No campaign data returned from Google Ads API")
            else:
                logger.error("Failed to create Google Ads client")
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            logger.error(traceback.format_exc())
            # Print more details about the client
            try:
                if client:
                    logger.error(f"Client type: {type(client)}")
                    logger.error(f"Client attributes: {dir(client)}")
            except:
                pass
    
    # If we get here, check if mock data is allowed
    if not ALLOW_MOCK_DATA:
        logger.error("Failed to get real campaign data and mock data is disabled")
        return jsonify({
            "error": "No data available",
            "message": "Failed to retrieve Google Ads campaign data and mock data is disabled in production mode",
            "environment": ENVIRONMENT
        }), 404
        
    # If mock data is allowed, generate and return it
    logger.info("Using mock campaign data")
    
    # Generate mock data
    mock_data = generate_mock_campaigns(10)
    
    return jsonify(mock_data)

@extended_bp.route('/ad_groups', methods=['GET'])
def get_ad_groups():
    """
    Get ad group performance data
    """
    # Get request parameters
    token = request.args.get('token')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    campaign_id = request.args.get('campaign_id')
    
    logger.info(f"Received request for ad groups with token: {token}")
    logger.info(f"USE_REAL_ADS_CLIENT is set to: {USE_REAL_ADS_CLIENT}")
    
    # Check if we should use real data
    use_real = USE_REAL_ADS_CLIENT or session.get('use_real_ads_client', False)
    logger.info(f"Using real data: {use_real}")
    
    # Try to get real data first
    if use_real and get_ad_group_performance and get_google_ads_client:
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
                    logger.warning("No ad group data returned from Google Ads API")
            else:
                logger.error("Failed to create Google Ads client")
        except Exception as e:
            logger.error(f"Error getting ad group data: {e}")
            logger.error(traceback.format_exc())
    
    # If we get here, check if mock data is allowed
    if not ALLOW_MOCK_DATA:
        logger.error("Failed to get real ad group data and mock data is disabled")
        return jsonify({
            "error": "No data available",
            "message": "Failed to retrieve Google Ads ad group data and mock data is disabled in production mode",
            "environment": ENVIRONMENT
        }), 404
        
    # If mock data is allowed, generate and return it
    logger.info("Using mock ad group data")
    
    # Generate mock data
    mock_data = generate_mock_ad_groups(campaign_id, 5)
    
    return jsonify(mock_data)

@extended_bp.route('/search_terms', methods=['GET'])
def get_search_terms():
    """
    Get search terms performance data
    """
    # Get date range and campaign ID from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    campaign_id = request.args.get('campaign_id')
    
    # Check if we should use real data
    use_real_data = False
    
    # Check if the request has a valid token
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        # Check if it's a real token or if we should force using real data
        if not token.startswith('mock-token') or session.get('use_real_ads_client', False):
            use_real_data = True
    
    # Try to get real data if we have a valid token
    if use_real_data and get_search_term_performance:
        try:
            search_terms_data = get_search_term_performance(start_date, end_date, campaign_id)
            if search_terms_data:
                return jsonify(search_terms_data)
        except Exception as e:
            logger.error(f"Error fetching search term data: {e}")
    
    # If we get here, check if mock data is allowed
    if not ALLOW_MOCK_DATA:
        logger.error("Failed to get real search term data and mock data is disabled")
        return jsonify({
            "error": "No data available",
            "message": "Failed to retrieve Google Ads search term data and mock data is disabled in production mode",
            "environment": ENVIRONMENT
        }), 404
        
    logger.info("Unable to fetch real search term data, returning N/A values with mock data")
    return jsonify(create_na_response("search_term"))

@extended_bp.route('/keywords', methods=['GET'])
def get_keywords():
    """
    Get keyword performance data
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get date range and ad group ID from request params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ad_group_id = request.args.get('ad_group_id')
    
    # Try to get real data first
    if get_search_term_performance:
        try:
            real_data = get_search_term_performance(start_date, end_date, ad_group_id)
            if real_data:
                return jsonify(real_data)
        except Exception as e:
            logger.error(f"Error fetching real keyword data: {e}")
    
    # If we get here, check if mock data is allowed
    if not ALLOW_MOCK_DATA:
        logger.error("Failed to get real keyword data and mock data is disabled")
        return jsonify({
            "error": "No data available",
            "message": "Failed to retrieve Google Ads keyword data and mock data is disabled in production mode",
            "environment": ENVIRONMENT
        }), 404
        
    logger.info("Unable to fetch real keyword data, returning N/A values with mock data")
    return jsonify(create_na_response("keyword"))

@extended_bp.route('/ads', methods=['GET'])
def get_ads():
    """
    Get ad performance data
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get date range and ad group ID from request params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ad_group_id = request.args.get('ad_group_id')
    
    # Try to get real data first
    if get_search_term_performance:
        try:
            real_data = get_search_term_performance(start_date) if start_date else None
            if real_data:
                return jsonify(real_data)
        except Exception as e:
            logger.error(f"Error fetching real ad performance data: {e}")
    
    # If we get here, check if mock data is allowed
    if not ALLOW_MOCK_DATA:
        logger.error("Failed to get real ad performance data and mock data is disabled")
        return jsonify({
            "error": "No data available",
            "message": "Failed to retrieve Google Ads ad performance data and mock data is disabled in production mode",
            "environment": ENVIRONMENT
        }), 404
        
    # Generate mock ad data if mock data is allowed
    logger.info("Generating mock ad performance data")
    
    # Generate mock ad data
    ad_types = ["Responsive Search Ad", "Expanded Text Ad", "Display Ad", "Video Ad"]
    statuses = ["ENABLED", "PAUSED", "REMOVED"]
    
    mock_ads = []
    for i in range(1, 6):  # Generate 5 mock ads
        # For testing, we'll generate different performance levels
        performance_tier = i % 3  # 0=high, 1=medium, 2=low
        
        # Base metrics adjusted by performance tier
        impressions = random.randint(1000, 5000) // (performance_tier + 1)
        clicks = random.randint(50, 500) // (performance_tier + 1)
        ctr = round(random.uniform(2, 15) / (performance_tier + 1), 2)
        conversions = random.randint(5, 50) // (performance_tier + 1)
        conv_rate = round(random.uniform(1, 10) / (performance_tier + 1), 2)
        cost = round(random.uniform(100, 1000) / (performance_tier + 1), 2)
        
        mock_ads.append({
            "ad_id": f"ad-{i}",
            "ad_type": random.choice(ad_types),
            "ad_group_id": ad_group_id or f"adgroup-{random.randint(1, 3)}",
            "headline": f"Sample Headline {i} - Click Here",
            "description": f"This is a sample description for ad {i}. Learn more about our products today!",
            "final_url": f"https://example.com/landing-page-{i}",
            "status": random.choice(statuses),
            "impressions": impressions,
            "clicks": clicks,
            "cost": cost,
            "conversions": conversions,
            "ctr": ctr,
            "cpc": round(cost / clicks if clicks > 0 else 0, 2),
            "conversion_rate": conv_rate,
            "cost_per_conversion": round(cost / conversions if conversions > 0 else 0, 2)
        })
    
    return jsonify(mock_ads)

@extended_bp.route('/performance', methods=['GET'])
def get_performance():
    """Get overall performance metrics from Google Ads API"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get date range from request params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Try to get real campaign data first
    if get_campaign_performance:
        try:
            campaigns = get_campaign_performance(start_date, end_date)
            if campaigns:
                # Aggregate metrics across all campaigns
                total_impressions = sum(campaign.get('summary', {}).get('impressions', 0) for campaign in campaigns)
                total_clicks = sum(campaign.get('summary', {}).get('clicks', 0) for campaign in campaigns)
                total_conversions = sum(campaign.get('summary', {}).get('conversions', 0) for campaign in campaigns)
                total_cost = sum(campaign.get('summary', {}).get('cost', 0) for campaign in campaigns)
                
                # Calculate derived metrics
                ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
                cost_per_conversion = (total_cost / total_conversions) if total_conversions > 0 else 0
                
                return jsonify({
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "conversions": total_conversions,
                    "cost": round(total_cost, 2),
                    "ctr": round(ctr, 2),
                    "conversion_rate": round(conversion_rate, 2),
                    "cost_per_conversion": round(cost_per_conversion, 2)
                })
        except Exception as e:
            logger.error(f"Error fetching real performance data: {e}")
    
    # If we get here, return N/A values
    logger.info("Unable to fetch real performance data, returning N/A values")
    return jsonify({
        "impressions": "N/A",
        "clicks": "N/A",
        "conversions": "N/A",
        "cost": "N/A",
        "ctr": "N/A",
        "conversion_rate": "N/A",
        "cost_per_conversion": "N/A"
    })

# Helper functions for generating mock data
def generate_mock_campaigns(count=10):
    """Generate mock campaign data"""
    campaigns = []
    for i in range(1, count + 1):
        campaign_id = f"campaign-{i}"
        campaigns.append({
            'id': campaign_id,
            'name': f"Mock Campaign {i}",
            'status': 'ENABLED',
            'impressions': random.randint(500, 5000),
            'clicks': random.randint(50, 500),
            'cost': round(random.uniform(100, 1000), 2),
            'ctr': round(random.uniform(1, 15), 2)
        })
    return campaigns

def generate_mock_ad_groups(campaign_id=None, count=5):
    """Generate mock ad group data"""
    ad_groups = []
    
    # If no campaign_id is provided, create mock ad groups for multiple campaigns
    if not campaign_id:
        campaigns = generate_mock_campaigns(3)
        for campaign in campaigns:
            for i in range(1, count + 1):
                ad_group_id = f"adgroup-{campaign['id']}-{i}"
                ad_groups.append({
                    'id': ad_group_id,
                    'name': f"Mock Ad Group {i} for {campaign['name']}",
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'status': 'ENABLED',
                    'impressions': random.randint(100, 1000),
                    'clicks': random.randint(10, 100),
                    'cost': round(random.uniform(50, 500), 2),
                    'ctr': round(random.uniform(1, 15), 2)
                })
    else:
        # Create mock ad groups for the specified campaign
        campaign_name = f"Campaign {campaign_id}"
        for i in range(1, count + 1):
            ad_group_id = f"adgroup-{campaign_id}-{i}"
            ad_groups.append({
                'id': ad_group_id,
                'name': f"Mock Ad Group {i} for {campaign_name}",
                'campaign_id': campaign_id,
                'campaign_name': campaign_name,
                'status': 'ENABLED',
                'impressions': random.randint(100, 1000),
                'clicks': random.randint(10, 100),
                'cost': round(random.uniform(50, 500), 2),
                'ctr': round(random.uniform(1, 15), 2)
            })
    
    return ad_groups
