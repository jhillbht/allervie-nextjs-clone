#!/usr/bin/env python3
"""
Test script for a single Google Ads API endpoint
This script allows testing individual endpoints with customizable parameters.
"""

import requests
import json
import argparse
from datetime import datetime, timedelta

# Available endpoints
ENDPOINTS = {
    "test": "/api/google-ads/test-connection",
    "simple": "/api/google-ads/simple-test",
    "performance": "/api/google-ads/performance",
    "campaigns": "/api/google-ads/campaigns",
    "ad_groups": "/api/google-ads/ad_groups",
    "search_terms": "/api/google-ads/search_terms",
    "keywords": "/api/google-ads/keywords",
    "ads": "/api/google-ads/ads",
    "available": "/api/google-ads/available_endpoints"
}

def get_default_date_params():
    """Generate default date parameters for API requests"""
    today = datetime.now().date()
    end_date = today - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=30)  # 30 days before end date
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }

def test_endpoint(base_url, endpoint_key, params=None, verbose=False):
    """Test a specific API endpoint with optional parameters"""
    if endpoint_key not in ENDPOINTS:
        print(f"Error: Unknown endpoint '{endpoint_key}'")
        print(f"Available endpoints: {', '.join(ENDPOINTS.keys())}")
        return False
    
    url = f"{base_url}{ENDPOINTS[endpoint_key]}"
    
    # If no params provided, use defaults for endpoints that need dates
    if params is None:
        params = {}
        if endpoint_key in ["performance", "campaigns", "ad_groups", "search_terms", "keywords", "ads"]:
            params.update(get_default_date_params())
    
    print(f"\n\033[1mTesting {endpoint_key} endpoint\033[0m")
    print(f"URL: {url}")
    if params:
        print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params)
        
        # Print response status
        print(f"Status code: {response.status_code}")
        
        # Handle successful response
        if response.status_code == 200:
            try:
                data = response.json()
                
                # In verbose mode, print the entire response
                if verbose:
                    print(f"Response data: {json.dumps(data, indent=2)}")
                else:
                    # Otherwise, print a summary or sample
                    if isinstance(data, list):
                        if len(data) > 0:
                            print(f"Returned {len(data)} items")
                            print(f"First item sample: {json.dumps(data[0], indent=2)}")
                        else:
                            print("Response is an empty list")
                    else:
                        # For dictionary responses, print a condensed version
                        print("Response summary:")
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, (dict, list)):
                                    if isinstance(value, dict):
                                        print(f"  {key}: {json.dumps(value, indent=2)}")
                                    else:  # list
                                        print(f"  {key}: List with {len(value)} items")
                                else:
                                    print(f"  {key}: {value}")
                        else:
                            print(f"Response data: {data}")
                
                print(f"\033[32mSuccess: {endpoint_key} endpoint test passed\033[0m")
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

def parse_params(param_strings):
    """Parse parameter strings in the format key=value"""
    params = {}
    if param_strings:
        for param in param_strings:
            parts = param.split('=', 1)
            if len(parts) == 2:
                key, value = parts
                params[key] = value
            else:
                print(f"Warning: Ignoring invalid parameter format: {param}")
    return params

def main():
    """Main function to parse arguments and test the endpoint"""
    parser = argparse.ArgumentParser(description="Test a specific Google Ads API endpoint")
    parser.add_argument("endpoint", choices=ENDPOINTS.keys(), 
                        help="The endpoint to test")
    parser.add_argument("--base-url", default="http://localhost:5002",
                        help="Base URL for the API (default: http://localhost:5002)")
    parser.add_argument("--param", action="append", dest="params",
                        help="Additional parameters in the format key=value (can be used multiple times)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print the full response data")
    
    args = parser.parse_args()
    
    # Parse parameters
    params = parse_params(args.params)
    
    # Test the endpoint
    success = test_endpoint(args.base_url, args.endpoint, params, args.verbose)
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())