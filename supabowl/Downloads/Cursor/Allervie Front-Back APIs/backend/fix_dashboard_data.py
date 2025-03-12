#!/usr/bin/env python
"""
Dashboard Data Enhancement for Allervie Analytics

This script helps improve the data quality in the Allervie Dashboard
after adding OAuth. It can be used to verify data retrieval, test API
endpoints, and optimize dashboard performance.
"""

import logging
import os
import sys
import traceback
from datetime import datetime, timedelta
import time
import json
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_all_endpoints():
    """Test all available API endpoints and measure response times"""
    results = {}
    endpoints = [
        'campaigns',
        'ad_groups',
        'search_terms',
        'keywords',
        'ads',
        'performance'
    ]
    
    for endpoint in endpoints:
        # Skip performance since it's handled separately
        if endpoint == 'performance':
            continue
            
        logger.info(f"Testing endpoint: {endpoint}")
        
        # Measure the response time
        start_time = time.time()
        try:
            # Try to import the module
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            # Try different data retrieval methods based on endpoint
            if endpoint == 'campaigns':
                from extended_google_ads_api import get_campaign_performance
                data = get_campaign_performance()
            elif endpoint == 'ad_groups':
                from extended_google_ads_api import get_ad_group_performance
                data = get_ad_group_performance()
            elif endpoint == 'search_terms' or endpoint == 'keywords':
                from extended_google_ads_api import get_search_term_performance
                data = get_search_term_performance()
            elif endpoint == 'ads':
                # Reusing search terms function for ads as per your code
                from extended_google_ads_api import get_search_term_performance
                data = get_search_term_performance()
            else:
                logger.error(f"Unknown endpoint: {endpoint}")
                continue
                
            elapsed_time = time.time() - start_time
            
            # Get data info
            if data:
                count = len(data)
                logger.info(f"Retrieved {count} items in {elapsed_time:.2f} seconds")
                results[endpoint] = {
                    "success": True,
                    "count": count,
                    "response_time": elapsed_time,
                    "message": f"Successfully retrieved {count} items"
                }
            else:
                logger.error(f"No data returned for {endpoint}")
                results[endpoint] = {
                    "success": False,
                    "count": 0,
                    "response_time": elapsed_time,
                    "message": "No data returned"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error testing {endpoint}: {e}")
            logger.error(traceback.format_exc())
            results[endpoint] = {
                "success": False,
                "count": 0,
                "response_time": elapsed_time,
                "message": f"Error: {str(e)}"
            }
    
    # Separately test performance endpoint which returns a dict, not a list
    try:
        from google_ads_client import get_ads_performance
        start_time = time.time()
        performance_data = get_ads_performance()
        elapsed_time = time.time() - start_time
        
        if performance_data:
            metrics_count = len(performance_data.keys())
            logger.info(f"Retrieved {metrics_count} performance metrics in {elapsed_time:.2f} seconds")
            results['performance'] = {
                "success": True,
                "metrics_count": metrics_count,
                "response_time": elapsed_time,
                "message": f"Successfully retrieved {metrics_count} metrics"
            }
        else:
            logger.error("No performance data returned")
            results['performance'] = {
                "success": False,
                "metrics_count": 0,
                "response_time": elapsed_time,
                "message": "No performance data returned"
            }
    except Exception as e:
        elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
        logger.error(f"Error testing performance endpoint: {e}")
        logger.error(traceback.format_exc())
        results['performance'] = {
            "success": False,
            "metrics_count": 0,
            "response_time": elapsed_time,
            "message": f"Error: {str(e)}"
        }
    
    return results

def test_different_date_ranges():
    """Test data retrieval with different date ranges"""
    date_ranges = [
        # Last 7 days
        (datetime.now() - timedelta(days=7), datetime.now()),
        # Last 30 days
        (datetime.now() - timedelta(days=30), datetime.now()),
        # Last 90 days
        (datetime.now() - timedelta(days=90), datetime.now()),
        # Year to date
        (datetime(datetime.now().year, 1, 1), datetime.now()),
    ]
    
    results = {}
    
    for start_date, end_date in date_ranges:
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        range_name = f"{start_str} to {end_str}"
        logger.info(f"Testing date range: {range_name}")
        
        # Measure response time for campaigns endpoint with this date range
        try:
            from extended_google_ads_api import get_campaign_performance
            
            start_time = time.time()
            campaigns = get_campaign_performance(start_date=start_str, end_date=end_str)
            elapsed_time = time.time() - start_time
            
            if campaigns:
                logger.info(f"Retrieved {len(campaigns)} campaigns in {elapsed_time:.2f} seconds")
                results[range_name] = {
                    "success": True,
                    "count": len(campaigns),
                    "response_time": elapsed_time,
                    "message": f"Successfully retrieved {len(campaigns)} campaigns"
                }
            else:
                logger.error(f"No campaign data returned for {range_name}")
                results[range_name] = {
                    "success": False,
                    "count": 0,
                    "response_time": elapsed_time,
                    "message": "No campaign data returned"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"Error testing date range {range_name}: {e}")
            logger.error(traceback.format_exc())
            results[range_name] = {
                "success": False,
                "count": 0,
                "response_time": elapsed_time,
                "message": f"Error: {str(e)}"
            }
    
    return results

def verify_token_auto_refresh():
    """Test that OAuth token auto-refresh is working properly"""
    # Import the auto refresh function
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import the token refresher
        from auto_refresh_token import refresh_token_if_needed
        
        # Check if token.json exists
        token_paths = [
            Path(__file__).parent.parent / "credentials" / "token.json",
            Path(__file__).parent / "token.json",
            Path.cwd() / "credentials" / "token.json",
            Path.cwd() / "token.json",
        ]
        
        token_path = None
        for path in token_paths:
            if path.exists():
                token_path = path
                break
        
        if not token_path:
            return {
                "success": False,
                "message": "No token.json file found"
            }
        
        # Get the current token data for comparison
        with open(token_path, 'r') as f:
            original_token_data = json.load(f)
        
        original_token = original_token_data.get('token', '')
        
        # Try to refresh the token
        logger.info("Testing token auto-refresh")
        result = refresh_token_if_needed()
        
        # Read the token file again to see if it changed
        with open(token_path, 'r') as f:
            new_token_data = json.load(f)
        
        new_token = new_token_data.get('token', '')
        
        # Compare tokens
        if original_token != new_token:
            logger.info("Token was refreshed successfully")
            return {
                "success": True,
                "token_changed": True,
                "message": "Token was successfully refreshed"
            }
        else:
            # Token might not need refresh yet
            logger.info("Token was not refreshed (might still be valid)")
            return {
                "success": True,
                "token_changed": False,
                "message": "Token not refreshed (might still be valid)"
            }
    except Exception as e:
        logger.error(f"Error testing token auto-refresh: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "message": f"Error testing token auto-refresh: {str(e)}"
        }

def diagnose_data_issues():
    """Run diagnostics to check for common data issues"""
    # Import required modules
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from extended_google_ads_api import get_campaign_performance
        from google_ads_client import get_google_ads_client
        
        issues = []
        
        # Test client creation
        client = get_google_ads_client()
        if not client:
            issues.append({
                "component": "GoogleAdsClient",
                "issue": "Failed to create Google Ads client",
                "severity": "High",
                "recommendation": "Check google-ads.yaml configuration and OAuth tokens"
            })
            return {
                "success": False,
                "issues": issues,
                "message": "Failed to create Google Ads client"
            }
        
        # Check if we can get basic campaign data
        campaigns = get_campaign_performance()
        if not campaigns:
            issues.append({
                "component": "CampaignData",
                "issue": "No campaign data retrieved",
                "severity": "High",
                "recommendation": "Check API access and permissions"
            })
        elif len(campaigns) == 0:
            issues.append({
                "component": "CampaignData",
                "issue": "Empty campaign data retrieved",
                "severity": "Medium",
                "recommendation": "Verify that this account has active campaigns"
            })
        
        # Try to get customer info
        try:
            customer_service = client.get_service('CustomerService')
            customer_id = client.login_customer_id
            resource_name = f"customers/{customer_id}"
            
            customer = customer_service.get_customer(resource_name=resource_name)
            if not customer:
                issues.append({
                    "component": "CustomerInfo",
                    "issue": "Could not retrieve customer information",
                    "severity": "Medium",
                    "recommendation": "Verify customer ID and permissions"
                })
        except Exception as e:
            issues.append({
                "component": "CustomerInfo",
                "issue": f"Error retrieving customer information: {str(e)}",
                "severity": "Medium",
                "recommendation": "Check customer ID and permissions"
            })
        
        # If no issues found
        if not issues:
            return {
                "success": True,
                "issues": [],
                "message": "No data issues detected"
            }
        
        return {
            "success": False,
            "issues": issues,
            "message": f"Found {len(issues)} issues with data retrieval"
        }
    except Exception as e:
        logger.error(f"Error diagnosing data issues: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "issues": [{
                "component": "DiagnosticsTool",
                "issue": f"Error running diagnostics: {str(e)}",
                "severity": "High",
                "recommendation": "Fix Python exceptions in the diagnostic code"
            }],
            "message": f"Error diagnosing data issues: {str(e)}"
        }

def main():
    """Run all tests and print results"""
    print("\n===== Allervie Dashboard Data Enhancement =====\n")
    
    # Test OAuth token auto-refresh
    print("\n----- OAuth Token Auto-Refresh -----")
    refresh_result = verify_token_auto_refresh()
    if refresh_result['success']:
        if refresh_result.get('token_changed', False):
            print("✅ OAuth token auto-refresh: Token was successfully refreshed")
        else:
            print("✅ OAuth token auto-refresh: Token is still valid (no refresh needed)")
    else:
        print(f"❌ OAuth token auto-refresh: {refresh_result['message']}")
    
    # Test all API endpoints
    print("\n----- API Endpoint Response Times -----")
    endpoint_results = test_all_endpoints()
    
    successful_endpoints = 0
    for endpoint, result in endpoint_results.items():
        if result['success']:
            successful_endpoints += 1
            if endpoint == 'performance':
                print(f"✅ {endpoint}: {result['metrics_count']} metrics in {result['response_time']:.2f}s")
            else:
                print(f"✅ {endpoint}: {result['count']} items in {result['response_time']:.2f}s")
        else:
            print(f"❌ {endpoint}: {result['message']}")
    
    # Test different date ranges
    print("\n----- Date Range Testing -----")
    date_range_results = test_different_date_ranges()
    
    successful_ranges = 0
    for range_name, result in date_range_results.items():
        if result['success']:
            successful_ranges += 1
            print(f"✅ {range_name}: {result['count']} campaigns in {result['response_time']:.2f}s")
        else:
            print(f"❌ {range_name}: {result['message']}")
    
    # Run diagnostics
    print("\n----- Data Issue Diagnostics -----")
    diagnostic_results = diagnose_data_issues()
    
    if diagnostic_results['success'] and not diagnostic_results.get('issues', []):
        print("✅ No data issues detected")
    else:
        for issue in diagnostic_results.get('issues', []):
            severity_icon = "⚠️" if issue['severity'] == "Medium" else "❌"
            print(f"{severity_icon} {issue['component']}: {issue['issue']}")
            print(f"   Recommendation: {issue['recommendation']}")
    
    # Overall assessment
    print("\n----- Overall Assessment -----")
    
    total_tests = len(endpoint_results) + len(date_range_results) + 1  # +1 for token refresh
    successful_tests = successful_endpoints + successful_ranges + (1 if refresh_result['success'] else 0)
    
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Success rate: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
    
    # Recommendations
    print("\n----- Recommendations -----")
    recommendations = []
    
    # Add recommendations based on test results
    if not refresh_result['success']:
        recommendations.append("- Fix OAuth token auto-refresh by running oauth_server.py")
    
    for endpoint, result in endpoint_results.items():
        if not result['success']:
            recommendations.append(f"- Fix {endpoint} endpoint data retrieval")
        elif result.get('response_time', 0) > 3:
            recommendations.append(f"- Optimize {endpoint} endpoint (response time: {result['response_time']:.2f}s)")
    
    for range_name, result in date_range_results.items():
        if not result['success']:
            recommendations.append(f"- Fix data retrieval for date range {range_name}")
    
    for issue in diagnostic_results.get('issues', []):
        recommendations.append(f"- {issue['recommendation']}")
    
    # Add a catch-all recommendation if all tests passed
    if not recommendations:
        recommendations.append("- Your dashboard data looks good! Consider adding user authentication for additional security")
        recommendations.append("- Monitor API quota usage regularly to avoid hitting limits")
    
    for recommendation in recommendations:
        print(recommendation)
    
    print("\n============================================\n")

if __name__ == "__main__":
    main()