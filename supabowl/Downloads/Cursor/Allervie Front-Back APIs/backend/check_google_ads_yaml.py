#!/usr/bin/env python
"""
Google Ads YAML Configuration Validator

This script checks the format of your google-ads.yaml file and helps
diagnose and fix common issues.
"""

import os
import sys
import yaml
from pathlib import Path
import re

def get_yaml_path():
    """Get the path to the google-ads.yaml file."""
    # Try to find the YAML file
    base_dir = Path(__file__).parent.parent
    credentials_dir = base_dir / 'credentials'
    
    # Check direct path
    yaml_path = credentials_dir / 'google-ads.yaml'
    if yaml_path.exists():
        return str(yaml_path)
    
    # Check in current directory
    if Path('google-ads.yaml').exists():
        return 'google-ads.yaml'
    
    raise FileNotFoundError("Could not find google-ads.yaml file")

def validate_yaml_file():
    """
    Validate the google-ads.yaml file and check for common issues.
    
    Returns:
        tuple: (is_valid, issues)
    """
    try:
        yaml_path = get_yaml_path()
        print(f"Checking YAML file at: {yaml_path}")
        
        with open(yaml_path, 'r') as f:
            content = f.read()
            
        # Try to parse the YAML
        try:
            config = yaml.safe_load(content)
            if not isinstance(config, dict):
                return False, ["YAML file does not contain a dictionary"]
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"]
        
        issues = []
        
        # Check required fields
        required_fields = ['developer_token', 'client_id', 'client_secret']
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            issues.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check for OAuth configuration
        oauth_fields = ['refresh_token']
        has_refresh_token = 'refresh_token' in config
        
        if not has_refresh_token:
            issues.append("Missing refresh_token - you need to authenticate with OAuth")
        
        # Check customer ID format
        if 'login_customer_id' in config:
            customer_id = str(config['login_customer_id'])
            if '-' in customer_id:
                issues.append(f"Customer ID ({customer_id}) contains dashes - remove them")
            if not re.match(r'^\d+$', customer_id):
                issues.append(f"Customer ID ({customer_id}) should contain only digits")
        else:
            issues.append("Missing login_customer_id")
        
        # Return validation result
        return len(issues) == 0, issues
    
    except FileNotFoundError:
        return False, ["google-ads.yaml file not found"]
    except Exception as e:
        return False, [f"Error validating YAML file: {e}"]

def fix_yaml_issues(issues):
    """
    Attempt to fix common issues with the YAML file.
    
    Args:
        issues (list): List of issues found by validate_yaml_file()
        
    Returns:
        bool: True if any fixes were applied
    """
    try:
        yaml_path = get_yaml_path()
        
        with open(yaml_path, 'r') as f:
            content = f.read()
            
        # Try to parse the YAML
        try:
            config = yaml.safe_load(content)
            if not isinstance(config, dict):
                return False
        except yaml.YAMLError:
            return False
        
        made_changes = False
        
        # Fix customer ID format if needed
        if 'login_customer_id' in config and '-' in str(config['login_customer_id']):
            customer_id = str(config['login_customer_id'])
            fixed_id = customer_id.replace('-', '')
            if re.match(r'^\d+$', fixed_id):
                print(f"Fixing customer ID: {customer_id} -> {fixed_id}")
                config['login_customer_id'] = fixed_id
                made_changes = True
        
        # Add use_proto_plus if missing
        if 'use_proto_plus' not in config:
            print("Adding use_proto_plus: True")
            config['use_proto_plus'] = True
            made_changes = True
        
        if made_changes:
            # Write updated YAML
            with open(yaml_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print(f"Updated {yaml_path} with fixes")
            return True
        
        return False
    
    except Exception as e:
        print(f"Error fixing YAML file: {e}")
        return False

def display_yaml_content():
    """Display the current content of the YAML file."""
    try:
        yaml_path = get_yaml_path()
        
        with open(yaml_path, 'r') as f:
            content = f.read()
        
        print("\nCurrent YAML content:")
        print("-" * 50)
        print(content)
        print("-" * 50)
    
    except Exception as e:
        print(f"Error reading YAML file: {e}")

def main():
    """Main function to validate the YAML file."""
    print("\n=== Google Ads YAML Configuration Validator ===\n")
    
    # Validate the YAML file
    is_valid, issues = validate_yaml_file()
    
    if is_valid:
        print("\n✅ YAML file is valid! Your Google Ads configuration looks good.")
        display_yaml_content()
        return 0
    
    # Display issues
    print("\n❌ Found issues with your Google Ads YAML configuration:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    # Try to fix issues
    if fix_yaml_issues(issues):
        print("\nSome issues have been automatically fixed.")
        is_valid, remaining_issues = validate_yaml_file()
        
        if is_valid:
            print("\n✅ YAML file is now valid!")
            display_yaml_content()
            return 0
        
        print("\nRemaining issues:")
        for i, issue in enumerate(remaining_issues, 1):
            print(f"  {i}. {issue}")
    
    # Provide guidance for manual fixes
    print("\nManual fixes required:")
    
    if any("refresh_token" in issue for issue in issues):
        print("\n1. To get a refresh token, run:")
        print("   python backend/get_refresh_token.py")
    
    if any("customer_id" in issue for issue in issues):
        print("\n2. Fix the customer ID format:")
        print("   - Remove any dashes from your customer ID")
        print("   - Make sure it contains only digits")
    
    if any("Missing required fields" in issue for issue in issues):
        print("\n3. Add the missing required fields to your YAML file:")
        print("   developer_token: YOUR_DEVELOPER_TOKEN")
        print("   client_id: YOUR_CLIENT_ID")
        print("   client_secret: YOUR_CLIENT_SECRET")
        print("   login_customer_id: YOUR_CUSTOMER_ID (without dashes)")
        print("   refresh_token: YOUR_REFRESH_TOKEN")
        print("   use_proto_plus: True")
    
    display_yaml_content()
    
    print("\nAfter making these changes, run this script again to validate.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
