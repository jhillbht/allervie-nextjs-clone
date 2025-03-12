#!/usr/bin/env python
"""
Test script for Google Ads Refresh Functionality

This script tests if the Google Ads refresh functionality is working correctly
by making API requests with different date ranges and verifying responses.
It now also tests OAuth token refresh and enhanced auto-refresh mechanisms.
"""

import requests
import json
import argparse
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = 'http://localhost:5002/api'

def format_date(date_obj):
    """Format a date object as YYYY-MM-DD string"""
    return date_obj.strftime('%Y-%m-%d')

def test_performance_endpoint(start_date=None, end_date=None):
    """Test the performance API endpoint"""
    if not start_date:
        start_date = format_date(datetime.now() - timedelta(days=30))
    if not end_date:
        end_date = format_date(datetime.now() - timedelta(days=1))
    
    print(f"\n=== Testing Performance Endpoint ===")
    print(f"Date range: {start_date} to {end_date}")
    
    url = f"{BASE_URL}/google-ads/performance?start_date={start_date}&end_date={end_date}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for non-200 responses
        
        data = response.json()
        print(f"Response status code: {response.status_code}")
        
        if 'error' in data:
            print(f"ERROR: {data.get('error')} - {data.get('message', 'No message')}")
            return False
        
        # Print metrics
        metrics = ['impressions', 'clicks', 'conversions', 'cost', 
                   'conversionRate', 'clickThroughRate', 'costPerConversion']
        
        for metric in metrics:
            if metric in data:
                value = data[metric].get('value', 'N/A')
                change = data[metric].get('change', 'N/A')
                print(f"{metric}: {value} (change: {change}%)")
            else:
                print(f"{metric}: Not available")
        
        return True
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_campaigns_endpoint(start_date=None, end_date=None):
    """Test the campaigns API endpoint"""
    if not start_date:
        start_date = format_date(datetime.now() - timedelta(days=30))
    if not end_date:
        end_date = format_date(datetime.now() - timedelta(days=1))
    
    print(f"\n=== Testing Campaigns Endpoint ===")
    print(f"Date range: {start_date} to {end_date}")
    
    url = f"{BASE_URL}/google-ads/campaigns?start_date={start_date}&end_date={end_date}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"Response status code: {response.status_code}")
        
        if isinstance(data, dict) and 'status' in data:
            if data['status'] == 'error':
                print(f"ERROR: {data.get('message', 'No message')}")
                return False
            
            campaigns = data.get('data', [])
            if not campaigns:
                print("No campaign data found")
                return False
            
            print(f"Received {len(campaigns)} campaigns")
            print("\nFirst 5 campaigns:")
            for i, campaign in enumerate(campaigns[:5]):
                print(f"{i+1}. {campaign.get('name')} - Impressions: {campaign.get('impressions')} - Clicks: {campaign.get('clicks')}")
            
            return True
        
        elif isinstance(data, list):
            if not data:
                print("No campaign data found")
                return False
            
            print(f"Received {len(data)} campaigns")
            print("\nFirst 5 campaigns:")
            for i, campaign in enumerate(data[:5]):
                print(f"{i+1}. {campaign.get('name')} - Impressions: {campaign.get('impressions')} - Clicks: {campaign.get('clicks')}")
            
            return True
        
        else:
            print(f"Unexpected response format: {data}")
            return False
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_token_refresh():
    """Test the OAuth token refresh functionality"""
    print("\n=== Testing OAuth Token Refresh ===")
    
    try:
        # Try to import the enhanced auto refresh module
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        try:
            # First try the enhanced refresh module
            from enhanced_auto_refresh import refresh_token_if_needed, find_token_file
            logger.info("Using enhanced_auto_refresh module")
        except ImportError:
            # Fall back to the standard module
            from auto_refresh_token import refresh_token_if_needed
            find_token_file = lambda: next((p for p in [
                Path(__file__).parent / "token.json",
                Path(__file__).parent.parent / "credentials" / "token.json",
                Path.cwd() / "token.json",
                Path.cwd() / "credentials" / "token.json"
            ] if p.exists()), None)
            logger.info("Using standard auto_refresh_token module")
        
        # Check if token file exists
        token_path = find_token_file()
        if not token_path:
            print("❌ Token file not found")
            return False
        
        # Read the original token file
        with open(token_path, 'r') as f:
            original_token_data = json.load(f)
        
        original_token = original_token_data.get('token', '')
        original_expiry = original_token_data.get('expiry', '')
        
        print(f"Original token: {original_token[:10]}...")
        print(f"Original expiry: {original_expiry}")
        
        # Force a token refresh
        print("Attempting to refresh token...")
        result = refresh_token_if_needed(force=True)
        
        if result:
            print("✅ Token refresh function reported success")
            
            # Read the new token
            with open(token_path, 'r') as f:
                new_token_data = json.load(f)
            
            new_token = new_token_data.get('token', '')
            new_expiry = new_token_data.get('expiry', '')
            
            print(f"New token: {new_token[:10]}...")
            print(f"New expiry: {new_expiry}")
            
            # Compare tokens
            if original_token != new_token:
                print("✅ Token was successfully refreshed (token changed)")
                return True
            else:
                print("⚠️ Token did not change after refresh")
                return False
        else:
            print("❌ Token refresh function reported failure")
            return False
    except Exception as e:
        print(f"❌ Error testing token refresh: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def run_all_tests():
    """Run all tests (token refresh and data refresh)"""
    # Test token refresh first
    token_refresh_result = test_token_refresh()
    
    # Run the data tests regardless of token refresh result
    run_data_tests()
    
    return token_refresh_result

def run_data_tests():
    """Run all tests with multiple date ranges"""
    print("\n=== STARTING DATA REFRESH FUNCTIONALITY TESTS ===")
    print("Testing with different date ranges to verify refresh functionality")
    
    today = datetime.now()
    
    # Test set 1: Last 30 days
    start1 = format_date(today - timedelta(days=30))
    end1 = format_date(today - timedelta(days=1))
    print(f"\n\n===== TEST SET 1: Last 30 days ({start1} to {end1}) =====")
    test_performance_endpoint(start1, end1)
    test_campaigns_endpoint(start1, end1)
    
    # Test set 2: Last 7 days
    start2 = format_date(today - timedelta(days=7))
    end2 = format_date(today - timedelta(days=1))
    print(f"\n\n===== TEST SET 2: Last 7 days ({start2} to {end2}) =====")
    test_performance_endpoint(start2, end2)
    test_campaigns_endpoint(start2, end2)
    
    # Test set 3: Previous 30 days
    start3 = format_date(today - timedelta(days=60))
    end3 = format_date(today - timedelta(days=31))
    print(f"\n\n===== TEST SET 3: Previous 30 days ({start3} to {end3}) =====")
    test_performance_endpoint(start3, end3)
    test_campaigns_endpoint(start3, end3)
    
    print("\n=== DATA TESTS COMPLETED ===")
    print("If you see different results between date ranges, then refresh is working")
    print("If all date ranges show identical results, the API might be caching or not using the dates correctly")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Google Ads API refresh functionality')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--all', action='store_true', help='Run all tests including OAuth and data tests')
    parser.add_argument('--token', action='store_true', help='Test only OAuth token refresh')
    parser.add_argument('--data', action='store_true', help='Test only data refresh with multiple date ranges')
    parser.add_argument('--url', default='http://localhost:5002/api', help='Base URL for API endpoints')
    
    args = parser.parse_args()
    
    # Update base URL if specified
    if args.url:
        BASE_URL = args.url
    
    # Determine which tests to run
    if args.all:
        run_all_tests()
    elif args.token:
        test_token_refresh()
    elif args.data:
        run_data_tests()
    else:
        # Default behavior - just test specific endpoints with specified dates
        test_performance_endpoint(args.start_date, args.end_date)
        test_campaigns_endpoint(args.start_date, args.end_date)