#!/bin/bash

# Script to get a real OAuth token for Google Ads API

echo "================================================================="
echo "Google OAuth Token Generator for Allervie Dashboard"
echo "================================================================="
echo ""
echo "This script will:
1. Start a local OAuth server on port 49153
2. Open your browser to authenticate with Google
3. Get a real OAuth token with the necessary scopes
4. Update your google-ads.yaml file with the new refresh token"
echo ""
echo "Note: You must log in with a Google account that has access to
the Google Ads account referenced in your google-ads.yaml file."
echo ""
echo "Press Enter to continue or Ctrl+C to exit..."
read

# Run the OAuth server
python backend/oauth_server.py

echo ""
echo "Once you have a valid refresh token, run the production server:"
echo "./run_production.sh"