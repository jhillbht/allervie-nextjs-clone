#!/usr/bin/env python
"""
List all accessible Google Ads customer accounts.

This script fetches and displays all customer accounts that are accessible
from the configured manager account.
"""

import os
import sys
import logging
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from pathlib import Path

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
                return client
            except Exception as e:
                logger.error(f"Error creating client: {e}")
                return None
    
    logger.error("Could not find google-ads.yaml in any expected location")
    return None

def list_accessible_customers():
    """Lists all accessible Google Ads customers."""
    # Get the Google Ads client
    client = get_google_ads_client()
    if not client:
        logger.error("Failed to create Google Ads client")
        return
    
    try:
        # Get the CustomerService
        customer_service = client.get_service("CustomerService")
        
        # Get accessible customers
        accessible_customers = customer_service.list_accessible_customers()
        
        # Extract customer resource names
        resource_names = accessible_customers.resource_names
        
        logger.info(f"Found {len(resource_names)} accessible customers")
        
        # Initialize a counter for valid accounts with detailed info
        valid_accounts = 0
        
        if not resource_names:
            logger.info("No accessible customers found")
            return
        
        print("\nAccessible Customer Accounts:")
        print("=" * 80)
        
        # Get the GoogleAdsService for more detailed queries
        googleads_service = client.get_service("GoogleAdsService")
        
        # Process each customer resource name
        for resource_name in resource_names:
            # Extract customer ID from resource name (format: "customers/{customer_id}")
            customer_id = resource_name.split('/')[1]
            
            # Query for more details about this customer
            try:
                query = """
                SELECT
                  customer.id,
                  customer.descriptive_name,
                  customer.currency_code,
                  customer.time_zone,
                  customer.manager
                FROM customer
                LIMIT 1
                """
                
                # Execute the query
                search_request = client.get_type("SearchGoogleAdsRequest")
                search_request.customer_id = customer_id
                search_request.query = query
                
                response = googleads_service.search(request=search_request)
                
                # Process the response
                for row in response:
                    customer = row.customer
                    is_manager = customer.manager if hasattr(customer, "manager") else False
                    
                    print(f"Customer ID: {customer.id}")
                    print(f"Name: {customer.descriptive_name}")
                    print(f"Currency: {customer.currency_code}")
                    print(f"Timezone: {customer.time_zone}")
                    print(f"Manager Account: {'Yes' if is_manager else 'No'}")
                    print("-" * 80)
                    
                    valid_accounts += 1
                    
            except GoogleAdsException as ex:
                print(f"Customer ID: {customer_id}")
                print(f"Error accessing customer details: {ex.error.message}")
                print("-" * 80)
        
        print(f"\nSuccessfully retrieved details for {valid_accounts} accounts")
        
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex}")
        for error in ex.failure.errors:
            logger.error(f"\tError with message: {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    logger.error(f"\t\tOn field: {field_path_element.field_name}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    list_accessible_customers()