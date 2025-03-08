#!/usr/bin/env python
"""
Simple script to verify the Google Ads YAML file can be loaded correctly.
"""

import yaml
import sys
from pathlib import Path

# Get the path to the YAML file
yaml_path = Path(__file__).parent.parent / "credentials" / "google-ads.yaml"
print(f"Checking YAML file at: {yaml_path}")

try:
    # Read the file content
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    print("\nFile content:")
    print("-" * 50)
    print(content)
    print("-" * 50)
    
    # Try to parse it as YAML
    config = yaml.safe_load(content)
    
    print("\nParsed YAML structure:")
    for key, value in config.items():
        if key == 'refresh_token':
            # Truncate the refresh token for display
            value_display = value[:10] + "..." + value[-10:] if value else "None"
            print(f"{key}: {value_display}")
        else:
            print(f"{key}: {value}")
    
    # Check specifically for refresh_token
    if 'refresh_token' in config and config['refresh_token']:
        print("\n✅ refresh_token is present and not empty")
        print(f"Token length: {len(str(config['refresh_token']))} characters")
    else:
        print("\n❌ refresh_token is missing or empty")
    
    # Exit with success
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    sys.exit(1)
