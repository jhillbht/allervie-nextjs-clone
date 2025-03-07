#!/bin/bash

# Allervie Dashboard - Production Run Script
# This script starts the Allervie Dashboard in production mode 
# with no mock data or mock authentication.

# Set production environment variables
export FLASK_ENV=production

# Update config.py with production settings
echo "# Global configuration variables

# Set to True to always attempt to use real Google Ads data
# instead of mock data, even with mock authentication tokens
USE_REAL_ADS_CLIENT = True

# Set to False to disable all mock data functionality
ALLOW_MOCK_DATA = False

# Set to False to disable mock authentication tokens
ALLOW_MOCK_AUTH = False

# Set environment (development or production)
ENVIRONMENT = \"production\"" > backend/config.py

echo "==============================================="
echo "Starting Allervie Dashboard in PRODUCTION mode"
echo "==============================================="
echo "- ALL MOCK DATA COMPLETELY REMOVED"
echo "- ALL MOCK AUTH COMPLETELY REMOVED"
echo "- USING REAL GOOGLE ADS API DATA ONLY"
echo "- FAILURES WILL RETURN PROPER ERRORS"
echo "==============================================="

# Check if Google Ads credentials are properly configured
echo "Checking Google Ads API connection..."
python backend/test_ads_connection.py

# Start the backend server
echo "Starting backend server in production mode..."
cd backend
python app.py &
BACKEND_PID=$!

# Wait for the backend to start
echo "Waiting for backend to start..."
sleep 5

# Open the API test page in the default browser
echo "Opening API test page..."
open http://localhost:5002/api-endpoints

# Instructions for the user
echo ""
echo "===================================================="
echo "Allervie Dashboard is now running in PRODUCTION mode"
echo "===================================================="
echo ""
echo "Backend server is running at: http://localhost:5002"
echo "API endpoints documentation: http://localhost:5002/api-endpoints"
echo ""
echo "TEST THE /api/google-ads/performance ENDPOINT:"
echo ""
echo "1. First get a real OAuth token:"
echo "   curl -v http://localhost:5002/api/auth/login"
echo "   (Follow the OAuth flow in your browser)"
echo ""
echo "2. Use the token to call the performance endpoint:"
echo "   curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:5002/api/google-ads/performance"
echo ""
echo "Remember, in production mode:"
echo "- ONLY real Google OAuth authentication is accepted"
echo "- ALL mock functionality has been completely removed"
echo "- All API failures will return proper error responses"
echo ""
echo "Press Ctrl+C to stop the servers"

# Wait for user to press Ctrl+C
wait $BACKEND_PID