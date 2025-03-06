#!/bin/bash

# Run the Allervie Dashboard with real Google Ads data (with fallback)

# Make sure the configuration is set to use real Ads data
echo "Setting configuration to use real Google Ads data..."
echo "USE_REAL_ADS_CLIENT = True" > backend/config.py

# Check if Google Ads credentials are properly configured
echo "Checking Google Ads API connection..."
python backend/test_ads_connection.py

# Start the backend server with real Ads data
echo "Starting backend server with real Ads data..."
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
echo "Allervie Dashboard is now running with real Google Ads data"
echo "===================================================="
echo ""
echo "Backend server is running at: http://localhost:5002"
echo "API test page is at: http://localhost:5002/test-api"
echo "API endpoints documentation: http://localhost:5002/api-endpoints"
echo ""
echo "Press Ctrl+C to stop the servers"

# Wait for user to press Ctrl+C
wait $BACKEND_PID