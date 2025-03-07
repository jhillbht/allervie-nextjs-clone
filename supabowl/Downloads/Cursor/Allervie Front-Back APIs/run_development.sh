#!/bin/bash

# Allervie Dashboard - Development Run Script
# This script starts the Allervie Dashboard in development mode
# with mock data and mock authentication allowed as fallbacks.

# Set development environment variables
export FLASK_ENV=development

# Update config.py with development settings
echo "# Global configuration variables

# Set to True to always attempt to use real Google Ads data
# instead of mock data, even with mock authentication tokens
USE_REAL_ADS_CLIENT = True

# Set to True to allow fallback to mock data
ALLOW_MOCK_DATA = True

# Set to True to allow mock authentication
ALLOW_MOCK_AUTH = True

# Set environment (development or production)
ENVIRONMENT = \"development\"" > backend/config.py

echo "================================================="
echo "Starting Allervie Dashboard in DEVELOPMENT mode"
echo "================================================="
echo "- Mock data ENABLED as fallback"
echo "- Mock authentication ENABLED for testing"
echo "- Will try to use real Google Ads API data first"
echo "================================================="

# Check if Google Ads credentials are properly configured
echo "Checking Google Ads API connection..."
python backend/test_ads_connection.py

# Start the backend server
echo "Starting backend server in development mode..."
cd backend
python app.py &
BACKEND_PID=$!

# Wait for the backend to start
echo "Waiting for backend to start..."
sleep 5

# Open the API test page in the default browser
echo "Opening API test page..."
open http://localhost:5002/test-api

# Instructions for the user
echo ""
echo "===================================================="
echo "Allervie Dashboard is now running in DEVELOPMENT mode"
echo "===================================================="
echo ""
echo "Backend server is running at: http://localhost:5002"
echo "API test page is at: http://localhost:5002/test-api"
echo "API endpoints documentation: http://localhost:5002/api-endpoints"
echo ""
echo "For testing with mock auth, use: http://localhost:5002/api/auth/mock-token"
echo ""
echo "Press Ctrl+C to stop the servers"

# Wait for user to press Ctrl+C
wait $BACKEND_PID