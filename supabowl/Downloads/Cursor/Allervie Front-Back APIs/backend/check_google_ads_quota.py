#!/usr/bin/env python3
"""
Google Ads API Quota Monitoring Script

This script checks the current quota usage for the Google Ads API
and provides warnings if approaching limits.
"""

import os
import sys
import logging
import time
from datetime import datetime
from pathlib import Path
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
except ImportError:
    logger.error("Failed to import Google Ads API libraries. Please install with: pip install google-ads")
    sys.exit(1)

# Constants
DEFAULT_LOG_FILE = 'quota_usage.json'

def get_google_ads_client():
    """Create a Google Ads API client."""
    try:
        # Try different locations for the google-ads.yaml file
        possible_paths = [
            Path(__file__).parent.parent / "credentials" / "google-ads.yaml",
            Path(__file__).parent / "google-ads.yaml",
            Path.cwd() / "credentials" / "google-ads.yaml",
            Path.cwd() / "google-ads.yaml",
        ]
        
        yaml_path = None
        for path in possible_paths:
            if path.exists():
                yaml_path = str(path)
                logger.info(f"Found google-ads.yaml at: {yaml_path}")
                break
        
        if not yaml_path:
            logger.error("google-ads.yaml not found in any of the expected locations")
            return None
        
        # Load the client
        client = GoogleAdsClient.load_from_storage(yaml_path)
        logger.info("Successfully created Google Ads client")
        return client
        
    except Exception as e:
        logger.error(f"Error creating Google Ads client: {e}")
        return None

def check_api_status(client):
    """Check the Google Ads API status and quota usage."""
    if not client:
        logger.error("No Google Ads client provided")
        return None
    
    try:
        # Get the customer ID from config or client
        try:
            from config import CLIENT_CUSTOMER_ID
            customer_id = CLIENT_CUSTOMER_ID
            logger.info(f"Using client account ID from config: {customer_id}")
        except ImportError:
            customer_id = client.login_customer_id
            logger.info(f"Using customer ID from client: {customer_id}")
        
        # Get the API service
        service = client.get_service("GoogleAdsService")
        
        # Create a simple query to test the API
        query = """
            SELECT 
                customer.id
            FROM customer
            LIMIT 1
        """
        
        # Track start time for latency measurement
        start_time = time.time()
        
        # Execute the query
        try:
            response = service.search(
                customer_id=customer_id,
                query=query
            )
            
            # Calculate latency
            latency = time.time() - start_time
            
            # Convert response to list to force execution
            results = list(response)
            
            # Create status report
            status = {
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "latency_seconds": round(latency, 3),
                "customer_id": customer_id,
                "query_complexity": "low",  # Simple query
                "api_version": getattr(client, 'version', 'unknown'),
                "error": None
            }
            
            return status
            
        except GoogleAdsException as gae:
            # Handle Google Ads API specific errors
            errors = []
            for error in gae.failure.errors:
                errors.append({
                    "error_code": error.error_code.name,
                    "message": error.message,
                    "quota_impact": "unknown"  # Google doesn't directly expose quota impact
                })
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "latency_seconds": round(time.time() - start_time, 3),
                "customer_id": customer_id,
                "error": errors
            }
            
            return status
            
    except Exception as e:
        logger.error(f"Error checking API status: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": str(e)
        }

def calculate_daily_usage(log_file=DEFAULT_LOG_FILE):
    """Calculate the daily API usage based on logged data."""
    try:
        if not os.path.exists(log_file):
            return {
                "api_calls_today": 0,
                "estimated_quota_usage": 0,
                "first_call_today": datetime.now().isoformat(),
                "latest_call": None,
                "success_rate": 100.0
            }
        
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        # Filter logs for today
        today = datetime.now().date()
        today_logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]).date() == today]
        
        if not today_logs:
            return {
                "api_calls_today": 0,
                "estimated_quota_usage": 0,
                "first_call_today": datetime.now().isoformat(),
                "latest_call": None,
                "success_rate": 100.0
            }
        
        # Calculate metrics
        total_calls = len(today_logs)
        successful_calls = sum(1 for log in today_logs if log["success"])
        
        # Estimate quota usage (rough estimate)
        # Simple queries use approximately 1-10 quota units
        estimated_quota = total_calls * 5  # Average of 5 units per call
        
        return {
            "api_calls_today": total_calls,
            "estimated_quota_usage": estimated_quota,
            "first_call_today": today_logs[0]["timestamp"],
            "latest_call": today_logs[-1]["timestamp"],
            "success_rate": (successful_calls / total_calls) * 100 if total_calls > 0 else 100.0
        }
        
    except Exception as e:
        logger.error(f"Error calculating daily usage: {e}")
        return {
            "error": str(e),
            "api_calls_today": 0,
            "estimated_quota_usage": 0
        }

def log_api_usage(status, log_file=DEFAULT_LOG_FILE):
    """Log the API usage to a file."""
    try:
        # Create or load existing logs
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new log entry
        logs.append(status)
        
        # Keep only the last 1000 entries to avoid huge log files
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Write back to file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
        logger.info(f"API usage logged to {log_file}")
        
    except Exception as e:
        logger.error(f"Error logging API usage: {e}")

def print_quota_status(usage):
    """Print the quota status in a user-friendly format."""
    print("\n" + "="*50)
    print(" GOOGLE ADS API QUOTA STATUS ")
    print("="*50)
    print(f"API Calls Today: {usage['api_calls_today']}")
    print(f"Estimated Quota Usage: {usage['estimated_quota_usage']} units")
    
    # Daily quota limit is 15,000 units
    quota_percentage = (usage['estimated_quota_usage'] / 15000) * 100
    print(f"Quota Used: {quota_percentage:.2f}% of daily limit")
    
    # Display warning if approaching limit
    if quota_percentage > 80:
        print("\n⚠️  WARNING: Approaching daily quota limit!")
        print("Consider reducing API calls or implementing rate limiting.")
    elif quota_percentage > 50:
        print("\n⚠️  NOTICE: Using significant portion of daily quota.")
    
    print(f"\nSuccess Rate: {usage['success_rate']:.2f}%")
    
    if usage['latest_call']:
        print(f"Latest API Call: {usage['latest_call']}")
    
    print("="*50)

def main():
    """Main function to check Google Ads API quota."""
    print("Checking Google Ads API quota usage...")
    
    # Get Google Ads client
    client = get_google_ads_client()
    if not client:
        print("❌ Failed to create Google Ads client")
        return 1
    
    # Check API status
    status = check_api_status(client)
    if not status:
        print("❌ Failed to check API status")
        return 1
    
    # Log API usage
    log_api_usage(status)
    
    # Calculate and print daily usage
    usage = calculate_daily_usage()
    print_quota_status(usage)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())