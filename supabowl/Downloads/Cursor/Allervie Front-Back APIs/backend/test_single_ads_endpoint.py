#!/usr/bin/env python3
"""
Enhanced test for Google Ads API endpoints

This script provides comprehensive tests for Google Ads API endpoints
to verify that the integration is working correctly in production.
"""

import requests
import json
import sys
import os
import time
from datetime import datetime, timedelta

# Set the base URL for the API - default to the DO app URL for production testing
DEFAULT_URL = "https://allervie-unified.ondigitalocean.app"
BASE_URL = os.environ.get('API_URL', DEFAULT_URL)

def get_date_range():
    """Get a suitable date range for testing (last month)"""
    today = datetime.now()
    first_day_last_month = today.replace(day=1) - timedelta(days=1)
    first_day_last_month = first_day_last_month.replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    
    start_date = first_day_last_month.strftime('%Y-%m-%d')
    end_date = last_day_last_month.strftime('%Y-%m-%d')
    
    return start_date, end_date

def test_health_check():
    """Test the API health endpoint"""
    endpoint = f"{BASE_URL}/api/health"
    
    print(f"\n🔍 Testing health endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Status: {data.get('status')}")
            print(f"Environment: {data.get('environment')}")
            print(f"Version: {data.get('version')}")
            print("✅ Health check successful!")
            return True
        else:
            print("❌ Health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

def test_google_ads_test_connection():
    """Test the Google Ads connection test endpoint"""
    endpoint = f"{BASE_URL}/api/google-ads/test-connection"
    
    print(f"\n🔍 Testing Google Ads connection: {endpoint}")
    
    try:
        # Create a session for cookies
        session = requests.Session()
        
        # First, visit the dashboard page to get a session cookie (auto-login in development mode)
        session.get(f"{BASE_URL}/ads-dashboard")
        
        response = session.get(endpoint)
        print(f"Status code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Connection status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            if data.get('status') == 'success':
                print(f"Customer ID: {data.get('customer_id')}")
                print("✅ Google Ads connection test successful!")
                return True
            else:
                print(f"Error: {data.get('message')}")
                print("❌ Google Ads connection test failed!")
                return False
        except:
            print("Raw response:")
            print(response.text)
            print("❌ Google Ads connection test failed!")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_simple_ads_test():
    """Test the simple Google Ads test endpoint"""
    endpoint = f"{BASE_URL}/api/google-ads/simple-test"
    
    print(f"\n🔍 Testing simple Google Ads test: {endpoint}")
    
    try:
        # Create a session for cookies
        session = requests.Session()
        
        # First, visit the dashboard page to get a session cookie (auto-login in development mode)
        session.get(f"{BASE_URL}/ads-dashboard")
        
        response = session.get(endpoint)
        print(f"Status code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Test status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            if data.get('status') == 'success':
                print(f"API Version: {data.get('api_version')}")
                print(f"Library Version: {data.get('library_version')}")
                print(f"Service Status: {data.get('service_status')}")
                print("✅ Simple Google Ads test successful!")
                return True
            else:
                print(f"Error: {data.get('message')}")
                print("❌ Simple Google Ads test failed!")
                return False
        except:
            print("Raw response:")
            print(response.text)
            print("❌ Simple Google Ads test failed!")
            return False
    except Exception as e:
        print(f"❌ Error with simple test: {e}")
        return False

def test_ads_performance():
    """Test the Google Ads performance endpoint"""
    # Define the endpoint
    endpoint = f"{BASE_URL}/api/google-ads/performance"
    
    # Get date range for last month
    start_date, end_date = get_date_range()
    
    # Add parameters for date range
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'previous_period': 'true'
    }
    
    # Make the request
    print(f"\n🔍 Testing performance endpoint: {endpoint}")
    print(f"With date range: {start_date} to {end_date}")
    
    try:
        # Create a session for cookies
        session = requests.Session()
        
        # First, visit the dashboard page to get a session cookie (auto-login in development mode)
        session.get(f"{BASE_URL}/ads-dashboard")
        
        # Try to use real ads client if in development
        if "localhost" in BASE_URL:
            session.get(f"{BASE_URL}/api/auth/use-real-ads-client")
        
        response = session.get(endpoint, params=params)
        
        # Print the status code
        print(f"Status code: {response.status_code}")
        
        # Pretty print the JSON response
        try:
            data = response.json()
            print("Response data:")
            metrics = ["impressions", "clicks", "conversions", "cost", "clickThroughRate", "conversionRate", "costPerConversion"]
            
            for metric in metrics:
                if metric in data:
                    value = data[metric].get('value', 'N/A')
                    change = data[metric].get('change', 'N/A')
                    print(f"  {metric}: {value} (change: {change}%)")
            
            # Check if we got any real data
            has_real_data = any(
                isinstance(data.get(metric, {}).get('value'), (int, float)) and
                data.get(metric, {}).get('value') > 0
                for metric in metrics
            )
            
            if response.status_code == 200 and has_real_data:
                print("✅ Performance data test successful!")
                return True
            elif response.status_code == 200:
                print("⚠️ Endpoint returned 200 but no real data found")
                return False
            else:
                print("❌ Performance data test failed!")
                return False
            
        except Exception as parse_error:
            print("Error parsing response:")
            print(parse_error)
            print("Raw response:")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error making request: {e}")
        return False

def test_single_endpoint(endpoint, options=None):
    """Test a specific Google Ads API endpoint with custom options"""
    # Base URL for the Google Ads API
    api_base_url = f"{BASE_URL}/api/google-ads"
    
    # Start with default parameters
    params = {
        "start_date": "2025-02-01",
        "end_date": "2025-03-01"
    }
    
    # Add any additional options
    if options:
        for option in options:
            if "=" in option:
                key, value = option.split("=", 1)
                params[key] = value
    
    # Full URL with parameters
    url = f"{api_base_url}/{endpoint}"
    
    print(f"\n🔍 Testing custom endpoint: {url}")
    print(f"Parameters: {params}")
    
    try:
        # Create a session for cookies
        session = requests.Session()
        
        # First, visit the dashboard page to get a session cookie (auto-login in development mode)
        session.get(f"{BASE_URL}/ads-dashboard")
        
        # Now make the request with the session
        response = session.get(url, params=params)
        
        # Print status code
        print(f"Status code: {response.status_code}")
        
        # Pretty print JSON response
        if response.status_code == 200:
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
                print("✅ Custom endpoint test successful!")
                return True
            except json.JSONDecodeError:
                print("Error decoding JSON response")
                print(response.text)
                print("❌ Custom endpoint test failed!")
                return False
        else:
            print(f"Error: {response.text}")
            print("❌ Custom endpoint test failed!")
            return False
    except Exception as e:
        print(f"❌ Error making request: {e}")
        return False

def run_all_tests():
    """Run all tests in sequence and report overall status"""
    print("=" * 60)
    print("GOOGLE ADS API INTEGRATION TEST")
    print(f"Target API: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all tests
    health_ok = test_health_check()
    connection_ok = test_google_ads_test_connection()
    simple_test_ok = test_simple_ads_test()
    performance_ok = test_ads_performance()
    
    # Calculate overall status
    required_tests = [health_ok, connection_ok]  # Health and connection are required
    optional_tests = [simple_test_ok, performance_ok]  # Others are nice to have
    
    required_success = all(required_tests)
    optional_success = any(optional_tests)
    
    # Report overall status
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Google Ads Connection: {'✅' if connection_ok else '❌'}")
    print(f"Simple Google Ads Test: {'✅' if simple_test_ok else '❌'}")
    print(f"Performance Data Test: {'✅' if performance_ok else '❌'}")
    print("-" * 60)
    
    if required_success and optional_success:
        print("✅ All tests PASSED!")
        return 0
    elif required_success:
        print("⚠️ Basic connectivity PASSED but some data tests FAILED")
        return 1
    else:
        print("❌ Critical tests FAILED")
        return 2

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python test_single_ads_endpoint.py                # Run all tests")
        print("  python test_single_ads_endpoint.py [endpoint]     # Test a specific endpoint")
        print("  python test_single_ads_endpoint.py [endpoint] [options]  # Test with options")
        print("  python test_single_ads_endpoint.py --url=URL      # Use a custom base URL")
        print("\nAvailable endpoints:")
        print("  simple-test        # Basic API connection test")
        print("  test-connection    # Test Google Ads API connection")
        print("  performance        # Test performance metrics endpoint")
        print("  campaigns          # Test campaign listing endpoint")
        print("  ad_groups          # Test ad group listing endpoint")
        print("  search_terms       # Test search terms report endpoint")
        print("  keywords           # Test keywords report endpoint")
        print("  ads                # Test ads report endpoint")
        sys.exit(0)
    
    # Check for custom URL
    for arg in sys.argv:
        if arg.startswith("--url="):
            BASE_URL = arg.split("=", 1)[1]
            sys.argv.remove(arg)
            print(f"Using custom URL: {BASE_URL}")
            break
    
    # If no specific endpoint provided, run all tests
    if len(sys.argv) == 1:
        result = run_all_tests()
        sys.exit(result)
    else:
        # First argument is the endpoint
        endpoint = sys.argv[1]
        
        # All other arguments are options
        options = sys.argv[2:] if len(sys.argv) > 2 else None
        
        # Test the specified endpoint
        success = test_single_endpoint(endpoint, options)
        
        # Exit with appropriate status code
        sys.exit(0 if success else 1)
