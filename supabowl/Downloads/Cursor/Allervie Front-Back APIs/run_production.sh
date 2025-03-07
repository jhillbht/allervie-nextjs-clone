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
echo "- Mock data disabled"
echo "- Mock authentication disabled"
echo "- Using real Google Ads API data only"
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
echo "Remember, in production mode:"
echo "- You MUST use real Google OAuth authentication"
echo "- No mock data will be returned if real data is unavailable"
echo "- Any API errors will be returned as-is for debugging"
echo ""
echo "Press Ctrl+C to stop the servers"

# Wait for user to press Ctrl+C
wait $BACKEND_PID