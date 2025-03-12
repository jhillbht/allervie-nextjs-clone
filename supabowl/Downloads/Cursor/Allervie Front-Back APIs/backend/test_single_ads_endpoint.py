#\!/usr/bin/env python3
"""
Test a single Google Ads API endpoint
"""
import sys
import requests
import json
import time

def test_endpoint(endpoint, options=None):
    """Test a specific Google Ads API endpoint"""
    # Base URL for the API
    base_url = "http://localhost:5002/api/google-ads"
    
    # Start with default parameters
    params = {
        "start_date": "2025-02-07",
        "end_date": "2025-03-09"
    }
    
    # Add any additional options
    if options:
        for option in options:
            if "=" in option:
                key, value = option.split("=", 1)
                params[key] = value
    
    # Full URL with parameters
    url = f"{base_url}/{endpoint}"
    
    print(f"Testing endpoint: {url}")
    print(f"Parameters: {params}")
    
    try:
        # Create a session for cookies
        session = requests.Session()
        
        # First, visit the dashboard page to get a session cookie (auto-login in development mode)
        session.get("http://localhost:5002/ads-dashboard")
        
        # Now make the request with the session
        response = session.get(url, params=params)
        
        # Print status code
        print(f"Status code: {response.status_code}")
        
        # Pretty print JSON response
        if response.status_code == 200:
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
                return True
            except json.JSONDecodeError:
                print("Error decoding JSON response")
                print(response.text)
                return False
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error making request: {e}")
        return False

if __name__ == "__main__":
    # Get endpoint from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python test_single_ads_endpoint.py [endpoint] [options]")
        print("Available endpoints: simple-test, test-connection, performance, campaigns, ad_groups, search_terms, keywords, ads")
        sys.exit(1)
    
    # First argument is the endpoint
    endpoint = sys.argv[1]
    
    # All other arguments are options
    options = sys.argv[2:] if len(sys.argv) > 2 else None
    
    # Test the endpoint
    success = test_endpoint(endpoint, options)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
