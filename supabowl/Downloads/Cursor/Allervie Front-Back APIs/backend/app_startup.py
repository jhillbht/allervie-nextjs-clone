#!/usr/bin/env python
"""
App Startup Script for Allervie Analytics Dashboard

This script runs when the app starts up, handling initialization tasks:
1. Verifies OAuth tokens and refreshes if needed
2. Checks API connectivity
3. Sets up scheduled token refresh
4. Runs diagnostics on deployment environment

Include this in your app's startup sequence to ensure optimal configuration.
"""

import os
import sys
import logging
from pathlib import Path
import threading
import time
import importlib.util
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def import_module_from_path(module_name, file_path):
    """Dynamically import a module from file path"""
    try:
        if not Path(file_path).exists():
            logger.error(f"Module file not found: {file_path}")
            return None
            
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec:
            logger.error(f"Could not create spec for module: {file_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error importing module {module_name} from {file_path}: {e}")
        logger.error(traceback.format_exc())
        return None

def verify_oauth_setup():
    """Verify OAuth token setup and refresh if needed"""
    logger.info("Verifying OAuth token setup")
    
    try:
        # First try the enhanced refresh
        enhanced_refresh_path = str(Path(__file__).parent / "enhanced_auto_refresh.py")
        use_enhanced = os.environ.get('USE_ENHANCED_REFRESH', 'true').lower() == 'true'
        
        if use_enhanced and Path(enhanced_refresh_path).exists():
            logger.info("Using enhanced token refresh")
            enhanced_module = import_module_from_path("enhanced_auto_refresh", enhanced_refresh_path)
            
            if enhanced_module and hasattr(enhanced_module, 'refresh_token_if_needed'):
                result = enhanced_module.refresh_token_if_needed()
                if result:
                    logger.info("Enhanced token refresh check completed successfully")
                    return True
                else:
                    logger.warning("Enhanced token refresh check failed, falling back to standard refresh")
            else:
                logger.warning("Could not load enhanced_auto_refresh module properly")
        
        # Fall back to standard refresh
        regular_refresh_path = str(Path(__file__).parent / "auto_refresh_token.py")
        if Path(regular_refresh_path).exists():
            logger.info("Using standard token refresh")
            refresh_module = import_module_from_path("auto_refresh_token", regular_refresh_path)
            
            if refresh_module and hasattr(refresh_module, 'refresh_token_if_needed'):
                result = refresh_module.refresh_token_if_needed()
                if result:
                    logger.info("Standard token refresh check completed successfully")
                    return True
                else:
                    logger.error("Standard token refresh check failed")
                    return False
            else:
                logger.error("Could not load auto_refresh_token module properly")
                return False
        else:
            logger.error("No token refresh module found")
            return False
    except Exception as e:
        logger.error(f"Error verifying OAuth setup: {e}")
        logger.error(traceback.format_exc())
        return False

def verify_api_connectivity():
    """Test API connectivity to Google Ads"""
    logger.info("Testing API connectivity")
    
    try:
        # Try to import Google Ads client
        client_path = str(Path(__file__).parent / "google_ads_client.py")
        client_module = import_module_from_path("google_ads_client", client_path)
        
        if client_module and hasattr(client_module, 'get_google_ads_client'):
            client = client_module.get_google_ads_client()
            if client:
                logger.info("Successfully created Google Ads client")
                
                # Try a simple API call
                try:
                    service = client.get_service('GoogleAdsService')
                    customer_id = client.login_customer_id
                    
                    # Simple query to verify connectivity
                    query = """
                        SELECT customer.id
                        FROM customer
                        LIMIT 1
                    """
                    
                    response = service.search(
                        customer_id=customer_id,
                        query=query
                    )
                    
                    # Check if we got a response
                    for row in response:
                        logger.info(f"API connectivity verified with customer ID: {row.customer.id}")
                        return True
                    
                    logger.warning("API connectivity verified but no customer data returned")
                    return True
                except Exception as api_error:
                    logger.error(f"API connectivity test failed: {api_error}")
                    logger.error(traceback.format_exc())
                    return False
            else:
                logger.error("Failed to create Google Ads client")
                return False
        else:
            logger.error("Could not load google_ads_client module properly")
            return False
    except Exception as e:
        logger.error(f"Error verifying API connectivity: {e}")
        logger.error(traceback.format_exc())
        return False

def setup_scheduled_refresh():
    """Set up a background thread for scheduled token refresh"""
    if os.environ.get('TOKEN_AUTO_REFRESH_ENABLED', 'true').lower() != 'true':
        logger.info("Scheduled token refresh is disabled")
        return False
    
    try:
        # Get refresh interval from environment (default to 30 minutes)
        interval_minutes = int(os.environ.get('AUTO_REFRESH_INTERVAL_MINUTES', '30'))
        
        def refresh_task():
            """Background task to refresh token periodically"""
            logger.info(f"Starting scheduled token refresh (every {interval_minutes} minutes)")
            
            while True:
                # Sleep first, then refresh
                time.sleep(interval_minutes * 60)
                
                try:
                    logger.info("Running scheduled token refresh")
                    verify_oauth_setup()
                except Exception as e:
                    logger.error(f"Error in scheduled token refresh: {e}")
        
        # Start the background thread
        refresh_thread = threading.Thread(target=refresh_task, daemon=True)
        refresh_thread.start()
        
        logger.info(f"Scheduled token refresh started (every {interval_minutes} minutes)")
        return True
    except Exception as e:
        logger.error(f"Error setting up scheduled refresh: {e}")
        logger.error(traceback.format_exc())
        return False

def run_diagnostics():
    """Run diagnostics on the deployment environment"""
    logger.info("Running deployment diagnostics")
    
    try:
        # Check for diagnostic script
        diagnostic_path = str(Path(__file__).parent / "check_deployment.py")
        
        if Path(diagnostic_path).exists():
            logger.info("Loading diagnostics module")
            diagnostic_module = import_module_from_path("check_deployment", diagnostic_path)
            
            if diagnostic_module:
                # Check if yaml file is valid
                if hasattr(diagnostic_module, 'check_google_ads_yaml'):
                    yaml_valid, yaml_path, yaml_result = diagnostic_module.check_google_ads_yaml()
                    if yaml_valid:
                        logger.info(f"Google Ads YAML is valid: {yaml_path}")
                    else:
                        logger.error(f"Google Ads YAML issue: {yaml_result}")
                
                # Check environment variables
                if hasattr(diagnostic_module, 'check_env_vars'):
                    env_valid, env_message = diagnostic_module.check_env_vars()
                    if env_valid:
                        logger.info(f"Environment variables: {env_message}")
                    else:
                        logger.error(f"Environment variables: {env_message}")
                
                # Check token validity
                if hasattr(diagnostic_module, 'check_token_validity'):
                    token_valid, token_message = diagnostic_module.check_token_validity()
                    if token_valid:
                        logger.info(f"Token validity: {token_message}")
                    else:
                        logger.error(f"Token validity: {token_message}")
                
                logger.info("Diagnostics completed")
                return True
            else:
                logger.error("Could not load diagnostics module properly")
                return False
        else:
            logger.warning("Diagnostics module not found, skipping")
            return True
    except Exception as e:
        logger.error(f"Error running diagnostics: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to run all startup checks"""
    logger.info("Running app startup sequence")
    
    # Run startup tasks
    oauth_result = verify_oauth_setup()
    api_result = verify_api_connectivity()
    refresh_result = setup_scheduled_refresh()
    diagnostics_result = run_diagnostics()
    
    # Print summary
    logger.info("=== Startup Sequence Summary ===")
    logger.info(f"OAuth Token Verification: {'✓' if oauth_result else '✗'}")
    logger.info(f"API Connectivity: {'✓' if api_result else '✗'}")
    logger.info(f"Scheduled Refresh Setup: {'✓' if refresh_result else '✗'}")
    logger.info(f"Diagnostics: {'✓' if diagnostics_result else '✗'}")
    
    # Overall result
    if oauth_result and api_result:
        logger.info("Startup completed successfully!")
        return 0
    else:
        logger.error("Startup encountered issues. See logs for details.")
        return 1

if __name__ == "__main__":
    exit(main())