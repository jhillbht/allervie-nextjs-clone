"""
Extended Google Ads API Module

This module provides additional Google Ads API endpoints beyond the basic performance metrics.
It includes functions for retrieving campaign data, ad group data, keyword data, and more.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import from google_ads_client
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    from google_ads_client import get_google_ads_client  # Import the centralized client initialization
    logger.info("Successfully imported Google Ads API libraries")
except ImportError as e:
    logger.error(f"Failed to import Google Ads API libraries: {e}")
    GoogleAdsClient = None
    GoogleAdsException = Exception

def get_campaign_performance(client, days=30):
    """Get campaign performance data for the last 30 days"""
    try:
        if not client:
            logger.error("No Google Ads client provided")
            return None
            
        logger.info(f"Client type: {type(client).__name__}")
        
        # Get the Google Ads service
        google_ads_service = client.get_service("GoogleAdsService")
        logger.info(f"Got GoogleAdsService: {type(google_ads_service).__name__}")
        
        # Get the customer ID from the client
        customer_id = client.login_customer_id
        logger.info(f"Using customer ID: {customer_id}")
        
        # Calculate the date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Format the dates for the query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        logger.info(f"Querying data from {start_date_str} to {end_date_str}")
        
        # Build the query
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.ctr
            FROM campaign
            WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
            ORDER BY campaign.name
        """
        
        # Execute the query (trying both v17 and legacy approaches)
        logger.info("Executing Google Ads API query for campaigns")
        
        try:
            # First try the direct v17 style
            logger.info("Trying direct parameter style...")
            response = google_ads_service.search(
                customer_id=customer_id,
                query=query
            )
            logger.info("Direct parameter style succeeded")
        except Exception as e:
            logger.warning(f"Direct parameter style failed: {e}, trying legacy style")
            
            # Fall back to legacy style
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            response = google_ads_service.search(request=search_request)
            logger.info("Legacy parameter style succeeded")
        
        # Process the results
        campaigns = []
        row_count = 0
        
        for row in response:
            row_count += 1
            campaign = row.campaign
            metrics = row.metrics
            
            logger.info(f"Processing campaign: {campaign.name} (ID: {campaign.id})")
            
            # Check if this campaign is already in our list
            existing_campaign = next((c for c in campaigns if c['id'] == str(campaign.id)), None)
            
            if existing_campaign:
                # Update the existing campaign with additional metrics
                # Only add values that are present and valid
                if hasattr(metrics, 'impressions') and metrics.impressions is not None:
                    existing_campaign['impressions'] += metrics.impressions
                
                if hasattr(metrics, 'clicks') and metrics.clicks is not None:
                    existing_campaign['clicks'] += metrics.clicks
                
                if hasattr(metrics, 'cost_micros') and metrics.cost_micros is not None:
                    existing_campaign['cost'] += metrics.cost_micros / 1000000
            else:
                # Create a new campaign dictionary with only ID and name as required fields
                new_campaign = {
                    'id': str(campaign.id),
                    'name': campaign.name if hasattr(campaign, 'name') else "Unnamed Campaign",
                }
                
                # Add other attributes only if they exist and are valid
                if hasattr(campaign, 'status') and campaign.status is not None:
                    new_campaign['status'] = campaign.status.name
                else:
                    new_campaign['status'] = "N/A"
                
                if hasattr(metrics, 'impressions') and metrics.impressions is not None:
                    new_campaign['impressions'] = metrics.impressions
                else:
                    new_campaign['impressions'] = "N/A"
                    
                if hasattr(metrics, 'clicks') and metrics.clicks is not None:
                    new_campaign['clicks'] = metrics.clicks
                else:
                    new_campaign['clicks'] = "N/A"
                    
                if hasattr(metrics, 'cost_micros') and metrics.cost_micros is not None:
                    new_campaign['cost'] = metrics.cost_micros / 1000000  # Convert micros to dollars
                else:
                    new_campaign['cost'] = "N/A"
                    
                if hasattr(metrics, 'ctr') and metrics.ctr is not None:
                    new_campaign['ctr'] = metrics.ctr * 100  # Convert to percentage
                else:
                    new_campaign['ctr'] = "N/A"
                
                # Add the new campaign to our list
                campaigns.append(new_campaign)
        
        logger.info(f"Processed {row_count} rows from the response")
        logger.info(f"Successfully retrieved data for {len(campaigns)} campaigns")
        
        # Sort campaigns by name
        campaigns.sort(key=lambda x: x['name'])
        
        return campaigns
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex}")
        for error in ex.failure.errors:
            logger.error(f"\tError with message: {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    logger.error(f"\t\tOn field: {field_path_element.field_name}")
        return None
    except Exception as e:
        logger.error(f"Error getting campaign performance: {e}")
        logger.error(traceback.format_exc())
        return None

def get_ad_group_performance(client, days=30):
    """Get ad group performance data for the last 30 days"""
    try:
        if not client:
            logger.error("No Google Ads client provided")
            return None
        
        # Get the Google Ads service
        google_ads_service = client.get_service("GoogleAdsService")
        
        # Get the customer ID from the yaml file
        customer_id = client.login_customer_id
        logger.info(f"Using customer ID: {customer_id}")
        
        # Calculate the date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Format the dates for the query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        logger.info(f"Querying data from {start_date_str} to {end_date_str}")
        
        # Build the query
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                ad_group.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.ctr
            FROM ad_group
            WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
            ORDER BY campaign.name, ad_group.name
        """
        
        # Execute the query
        logger.info("Executing Google Ads API query for ad groups")
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        # Get the results
        response = google_ads_service.search(request=search_request)
        
        # Process the results
        ad_groups = []
        row_count = 0
        
        for row in response:
            row_count += 1
            campaign = row.campaign
            ad_group = row.ad_group
            metrics = row.metrics
            
            logger.info(f"Processing ad group: {ad_group.name} (ID: {ad_group.id}) in campaign: {campaign.name}")
            
            # Check if this ad group is already in our list
            existing_ad_group = next((ag for ag in ad_groups if ag['id'] == str(ad_group.id)), None)
            
            if existing_ad_group:
                # Update the existing ad group with additional metrics
                # Only add values that are present and valid
                if hasattr(metrics, 'impressions') and metrics.impressions is not None:
                    existing_ad_group['impressions'] += metrics.impressions
                
                if hasattr(metrics, 'clicks') and metrics.clicks is not None:
                    existing_ad_group['clicks'] += metrics.clicks
                
                if hasattr(metrics, 'cost_micros') and metrics.cost_micros is not None:
                    existing_ad_group['cost'] += metrics.cost_micros / 1000000
            else:
                # Create a new ad group dictionary with only ID and name as required fields
                new_ad_group = {
                    'id': str(ad_group.id),
                    'name': ad_group.name if hasattr(ad_group, 'name') else "Unnamed Ad Group",
                    'campaign_id': str(campaign.id),
                    'campaign_name': campaign.name if hasattr(campaign, 'name') else "Unnamed Campaign",
                }
                
                # Add other attributes only if they exist and are valid
                if hasattr(ad_group, 'status') and ad_group.status is not None:
                    new_ad_group['status'] = ad_group.status.name
                else:
                    new_ad_group['status'] = "N/A"
                
                if hasattr(metrics, 'impressions') and metrics.impressions is not None:
                    new_ad_group['impressions'] = metrics.impressions
                else:
                    new_ad_group['impressions'] = "N/A"
                    
                if hasattr(metrics, 'clicks') and metrics.clicks is not None:
                    new_ad_group['clicks'] = metrics.clicks
                else:
                    new_ad_group['clicks'] = "N/A"
                    
                if hasattr(metrics, 'cost_micros') and metrics.cost_micros is not None:
                    new_ad_group['cost'] = metrics.cost_micros / 1000000  # Convert micros to dollars
                else:
                    new_ad_group['cost'] = "N/A"
                    
                if hasattr(metrics, 'ctr') and metrics.ctr is not None:
                    new_ad_group['ctr'] = metrics.ctr * 100  # Convert to percentage
                else:
                    new_ad_group['ctr'] = "N/A"
                
                # Add the new ad group to our list
                ad_groups.append(new_ad_group)
        
        logger.info(f"Processed {row_count} rows from the response")
        logger.info(f"Successfully retrieved data for {len(ad_groups)} ad groups")
        
        # Sort ad groups by campaign name and then ad group name
        ad_groups.sort(key=lambda x: (x['campaign_name'], x['name']))
        
        return ad_groups
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex}")
        for error in ex.failure.errors:
            logger.error(f"\tError with message: {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    logger.error(f"\t\tOn field: {field_path_element.field_name}")
        return None
    except Exception as e:
        logger.error(f"Error getting ad group performance: {e}")
        logger.error(traceback.format_exc())
        return None

def get_search_term_performance(client, days=30):
    """Get search term performance data for the last 30 days"""
    try:
        if not client:
            logger.error("No Google Ads client provided")
            return None
        
        # Get the Google Ads service
        google_ads_service = client.get_service("GoogleAdsService")
        
        # Get the customer ID from the yaml file
        customer_id = client.login_customer_id
        logger.info(f"Using customer ID: {customer_id}")
        
        # Calculate the date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Format the dates for the query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        logger.info(f"Querying data from {start_date_str} to {end_date_str}")
        
        # Build the query
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                search_term_view.search_term,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.ctr
            FROM search_term_view
            WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
            ORDER BY metrics.impressions DESC
            LIMIT 1000
        """
        
        # Execute the query
        logger.info("Executing Google Ads API query for search terms")
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        # Get the results
        response = google_ads_service.search(request=search_request)
        
        # Process the results
        search_terms = []
        row_count = 0
        
        for row in response:
            row_count += 1
            campaign = row.campaign
            ad_group = row.ad_group
            search_term = row.search_term_view.search_term
            metrics = row.metrics
            
            logger.info(f"Processing search term: {search_term}")
            
            # Check if this search term is already in our list
            existing_term = next((st for st in search_terms if st['search_term'] == search_term and 
                                 st['campaign_id'] == str(campaign.id) and 
                                 st['ad_group_id'] == str(ad_group.id)), None)
            
            if existing_term:
                # Update the existing search term with additional metrics
                # Only add values that are present and valid
                if hasattr(metrics, 'impressions') and metrics.impressions is not None:
                    existing_term['impressions'] += metrics.impressions
                
                if hasattr(metrics, 'clicks') and metrics.clicks is not None:
                    existing_term['clicks'] += metrics.clicks
                
                if hasattr(metrics, 'cost_micros') and metrics.cost_micros is not None:
                    existing_term['cost'] += metrics.cost_micros / 1000000
            else:
                # Create a new search term dictionary with required fields
                new_term = {
                    'search_term': search_term,
                    'campaign_id': str(campaign.id),
                    'campaign_name': campaign.name if hasattr(campaign, 'name') else "Unnamed Campaign",
                    'ad_group_id': str(ad_group.id),
                    'ad_group_name': ad_group.name if hasattr(ad_group, 'name') else "Unnamed Ad Group",
                }
                
                # Add other metrics only if they exist and are valid
                if hasattr(metrics, 'impressions') and metrics.impressions is not None:
                    new_term['impressions'] = metrics.impressions
                else:
                    new_term['impressions'] = "N/A"
                    
                if hasattr(metrics, 'clicks') and metrics.clicks is not None:
                    new_term['clicks'] = metrics.clicks
                else:
                    new_term['clicks'] = "N/A"
                    
                if hasattr(metrics, 'cost_micros') and metrics.cost_micros is not None:
                    new_term['cost'] = metrics.cost_micros / 1000000  # Convert micros to dollars
                else:
                    new_term['cost'] = "N/A"
                    
                if hasattr(metrics, 'ctr') and metrics.ctr is not None:
                    new_term['ctr'] = metrics.ctr * 100  # Convert to percentage
                else:
                    new_term['ctr'] = "N/A"
                
                # Add the new search term to our list
                search_terms.append(new_term)
        
        logger.info(f"Processed {row_count} rows from the response")
        logger.info(f"Successfully retrieved data for {len(search_terms)} search terms")
        
        # Sort search terms by impressions (descending)
        search_terms.sort(key=lambda x: x['impressions'], reverse=True)
        
        return search_terms
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex}")
        for error in ex.failure.errors:
            logger.error(f"\tError with message: {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    logger.error(f"\t\tOn field: {field_path_element.field_name}")
        return None
    except Exception as e:
        logger.error(f"Error getting search term performance: {e}")
        logger.error(traceback.format_exc())
        return None
