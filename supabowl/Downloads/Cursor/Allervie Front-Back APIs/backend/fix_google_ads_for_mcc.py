#!/usr/bin/env python
"""
Fix Google Ads integration for Manager (MCC) accounts.

This script updates the Google Ads client configuration to properly handle
calls from a Manager account (MCC) by implementing client account selection.

When a Google Ads API is accessed with a Manager account, metrics can't be
directly requested from the manager account. Instead, you need to:
1. Get a list of accessible client accounts
2. Query each client account individually
3. Aggregate the results

This script demonstrates how to properly set up this workflow.
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_google_ads_client():
    """Create and return a Google Ads client."""
    # Look for credentials file in multiple locations
    possible_paths = [
        Path(__file__).parent.parent / "credentials" / "google-ads.yaml",
        Path(__file__).parent / "google-ads.yaml",
        Path.cwd() / "credentials" / "google-ads.yaml",
        Path.cwd() / "google-ads.yaml",
    ]
    
    for path in possible_paths:
        if path.exists():
            yaml_path = str(path)
            logger.info(f"Found google-ads.yaml at: {yaml_path}")
            
            try:
                # Load the client with v17 API version
                client = GoogleAdsClient.load_from_storage(yaml_path, version="v17")
                logger.info("Successfully created Google Ads client")
                return client, yaml_path
            except Exception as e:
                logger.error(f"Error creating client: {e}")
                return None, None
    
    logger.error("Could not find google-ads.yaml in any expected location")
    return None, None

def get_client_accounts():
    """Get accessible client accounts under the MCC account."""
    # Get the Google Ads client
    client, _ = get_google_ads_client()
    if not client:
        return []
    
    try:
        # Get the CustomerService
        customer_service = client.get_service("CustomerService")
        
        # Get accessible customers
        accessible_customers = customer_service.list_accessible_customers()
        resource_names = accessible_customers.resource_names
        
        logger.info(f"Found {len(resource_names)} accessible customers")
        
        # Extract customer IDs from resource names
        client_accounts = []
        for resource_name in resource_names:
            customer_id = resource_name.split('/')[1]
            client_accounts.append(customer_id)
        
        return client_accounts
        
    except Exception as e:
        logger.error(f"Error getting client accounts: {e}")
        logger.error(traceback.format_exc())
        return []

def get_first_valid_client_account():
    """Find the first valid client account that can be accessed for metrics."""
    client_accounts = get_client_accounts()
    if not client_accounts:
        logger.error("No client accounts found")
        return None
    
    client, _ = get_google_ads_client()
    if not client:
        return None
    
    manager_id = client.login_customer_id
    logger.info(f"Manager account ID: {manager_id}")
    
    # Try each client account
    for customer_id in client_accounts:
        if customer_id == manager_id:
            logger.info(f"Skipping manager account: {customer_id}")
            continue
            
        logger.info(f"Testing client account: {customer_id}")
        try:
            # Get the GoogleAdsService
            googleads_service = client.get_service("GoogleAdsService")
            
            # Test query to get basic metrics
            query = """
            SELECT
                metrics.impressions
            FROM campaign
            WHERE segments.date DURING LAST_30_DAYS
            LIMIT 1
            """
            
            # Execute the query
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            # Set login-customer-id in the header
            response = googleads_service.search(request=search_request)
            
            # If we get here, the account is valid
            logger.info(f"Found valid client account: {customer_id}")
            return customer_id
            
        except GoogleAdsException as ex:
            logger.warning(f"Error accessing client account {customer_id}: {ex.error.message}")
            continue
        except Exception as e:
            logger.warning(f"Unexpected error for client account {customer_id}: {e}")
            continue
    
    logger.error("No valid client accounts found for metrics")
    return None

def update_google_ads_yaml_with_client_account():
    """Update the google-ads.yaml file with a valid client account."""
    client, yaml_path = get_google_ads_client()
    if not client or not yaml_path:
        logger.error("Could not get Google Ads client or yaml path")
        return False
    
    # Get the current manager account ID
    manager_id = client.login_customer_id
    logger.info(f"Current login_customer_id: {manager_id}")
    
    # Get a valid client account
    client_id = get_first_valid_client_account()
    if not client_id:
        logger.error("No valid client account found")
        return False
    
    # Backup the original yaml file
    backup_path = f"{yaml_path}.bak"
    try:
        with open(yaml_path, 'r') as f:
            original_content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        logger.info(f"Created backup of google-ads.yaml at {backup_path}")
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False
    
    # Update the yaml file
    try:
        import yaml
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Save the original as a comment
        if 'login_customer_id' in config:
            config['# original_manager_id'] = config['login_customer_id']
        
        # Set the new client account ID
        config['login_customer_id'] = client_id
        
        # Write the updated config
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Updated google-ads.yaml with client account ID: {client_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating yaml file: {e}")
        logger.error(traceback.format_exc())
        
        # Try to restore the backup
        try:
            with open(backup_path, 'r') as f:
                backup_content = f.read()
            
            with open(yaml_path, 'w') as f:
                f.write(backup_content)
            
            logger.info("Restored original yaml file from backup")
        except Exception as restore_error:
            logger.error(f"Error restoring backup: {restore_error}")
        
        return False

def test_updated_configuration():
    """Test the updated configuration with a client account."""
    client, _ = get_google_ads_client()
    if not client:
        return False
    
    customer_id = client.login_customer_id
    logger.info(f"Testing updated configuration with customer ID: {customer_id}")
    
    try:
        # Get the GoogleAdsService
        googleads_service = client.get_service("GoogleAdsService")
        
        # Test query to get basic metrics
        query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        LIMIT 10
        """
        
        # Execute the query
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        response = googleads_service.search(request=search_request)
        
        # Process the results
        total_impressions = 0
        total_clicks = 0
        total_cost_micros = 0
        
        for row in response:
            metrics = row.metrics
            customer = row.customer
            total_impressions += metrics.impressions
            total_clicks += metrics.clicks
            total_cost_micros += metrics.cost_micros
        
        logger.info(f"Customer: {customer.descriptive_name} (ID: {customer.id})")
        logger.info(f"Total Impressions: {total_impressions}")
        logger.info(f"Total Clicks: {total_clicks}")
        logger.info(f"Total Cost: ${total_cost_micros/1000000:.2f}")
        
        return True
        
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex.error.message}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("\n====================================================")
    print("GOOGLE ADS MANAGER ACCOUNT (MCC) CONFIGURATION FIXER")
    print("====================================================\n")
    
    print("This script will update your Google Ads configuration to use a valid client account")
    print("instead of a Manager (MCC) account for metrics queries.\n")
    
    # Update the configuration
    if update_google_ads_yaml_with_client_account():
        print("\n✅ Successfully updated Google Ads configuration with a valid client account")
        
        # Test the updated configuration
        if test_updated_configuration():
            print("\n✅ Successfully tested the updated configuration")
            print("\nYou can now run the dashboard with real Google Ads data")
            print("Use the run_with_real_ads.sh script to start the application")
        else:
            print("\n❌ Failed to test the updated configuration")
            print("Please check the logs for more information")
    else:
        print("\n❌ Failed to update Google Ads configuration")
        print("Please check the logs for more information")