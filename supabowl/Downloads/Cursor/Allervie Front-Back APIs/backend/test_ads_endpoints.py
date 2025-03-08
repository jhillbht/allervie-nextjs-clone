#!/usr/bin/env python3
"""
Test script for Google Ads API endpoints
This script will test all the Google Ads API endpoints available in the Allervie API.
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:5002"
ENDPOINTS = [
    # Basic endpoints
    {"name": "Test Connection", "endpoint": "/api/google-ads/test-connection", "method": "GET"},
    {"name": "Simple Test", "endpoint": "/api/google-ads/simple-test", "method": "GET"},
    {"name": "Available Endpoints", "endpoint": "/api/google-ads/available_endpoints", "method": "GET"},
    
    # Performance data endpoints
    {"name": "Performance", "endpoint": "/api/google-ads/performance", "method": "GET", "params": {}},
    {"name": "Campaigns", "endpoint": "/api/google-ads/campaigns", "method": "GET", "params": {}},
    {"name": "Ad Groups", "endpoint": "/api/google-ads/ad_groups", "method": "GET", "params": {}},
    {"name": "Search Terms", "endpoint": "/api/google-ads/search_terms", "method": "GET", "params": {}},
    {"name": "Keywords", "endpoint": "/api/google-ads/keywords", "method": "GET", "params": {}},
    {"name": "Ads", "endpoint": "/api/google-ads/ads", "method": "GET", "params": {}}
]

def get_date_params():
    """Generate date parameters for API requests"""
    today = datetime.now().date()
    end_date = today - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=30)  # 30 days before end date
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }

def test_endpoint(endpoint_info):
    """Test a single API endpoint"""
    method = endpoint_info["method"]
    url = f"{BASE_URL}{endpoint_info['endpoint']}"
    
    # Add date parameters for endpoints that need them
    params = {}
    if "params" in endpoint_info:
        params = endpoint_info["params"].copy()
        
        # Add date parameters for endpoints that support them
        if endpoint_info["name"] in ["Performance", "Campaigns", "Ad Groups", "Search Terms", "Keywords", "Ads"]:
            params.update(get_date_params())
    
    print(f"\n\033[1mTesting {endpoint_info['name']} endpoint\033[0m")
    print(f"URL: {url}")
    print(f"Method: {method}")
    if params:
        print(f"Parameters: {params}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=params)
        else:
            print(f"Unsupported method: {method}")
            return False
        
        # Print response status
        print(f"Status code: {response.status_code}")
        
        # Handle successful response
        if response.status_code == 200:
            try:
                data = response.json()
                # Pretty print a small sample of the data
                if isinstance(data, list) and len(data) > 0:
                    sample = data[0] if len(data) > 0 else data
                    print(f"Data sample: {json.dumps(sample, indent=2)}")
                else:
                    print(f"Response data: {json.dumps(data, indent=2)}")
                print(f"\033[32mSuccess: {endpoint_info['name']} endpoint test passed\033[0m")
                return True
            except json.JSONDecodeError:
                print(f"\033[31mError: Response is not valid JSON\033[0m")
                print(f"Response: {response.text[:200]}...")
                return False
        else:
            # Handle error response
            try:
                error_data = response.json()
                print(f"\033[31mError: {error_data.get('error', 'Unknown error')}\033[0m")
                print(f"Message: {error_data.get('message', 'No message provided')}")
            except json.JSONDecodeError:
                print(f"\033[31mError: Status code {response.status_code}\033[0m")
                print(f"Response: {response.text[:200]}...")
            return False
    
    except requests.RequestException as e:
        print(f"\033[31mError: {str(e)}\033[0m")
        return False

def main():
    """Main function to test all endpoints"""
    successful_tests = 0
    total_tests = len(ENDPOINTS)
    
    print("\033[1m===== Testing Google Ads API Endpoints =====\033[0m")
    
    for endpoint in ENDPOINTS:
        if test_endpoint(endpoint):
            successful_tests += 1
    
    print(f"\n\033[1m===== Test Summary =====\033[0m")
    print(f"Total endpoints tested: {total_tests}")
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {total_tests - successful_tests}")
    
    if successful_tests == total_tests:
        print("\n\033[32mAll tests passed successfully!\033[0m")
        return 0
    else:
        print(f"\n\033[31m{total_tests - successful_tests} test(s) failed.\033[0m")
        return 1

if __name__ == "__main__":
    sys.exit(main())