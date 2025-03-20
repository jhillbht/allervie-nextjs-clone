#!/bin/bash
# Allervie Dashboard DigitalOcean Deployment Script
# This script handles the deployment of the Allervie Dashboard to DigitalOcean App Platform

set -e # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Dashboard DigitalOcean Deployment Script     ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Variables - You can modify these as needed
REPO_PATH="/Users/supabowl/Downloads/Cursor/allervie-nextjs-clone"
APP_NAME="allervie-analytics-dashboard"

# Change to the repository directory
echo -e "${YELLOW}Changing to repository directory: $REPO_PATH${NC}"
cd "$REPO_PATH" || { echo -e "${RED}Error: Could not change to repository directory${NC}"; exit 1; }

# Check if doctl is installed
echo -e "${YELLOW}Checking if doctl is installed...${NC}"
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}doctl is not installed. Please install it first.${NC}"
    echo -e "macOS: brew install doctl"
    echo -e "Linux: snap install doctl"
    echo -e "Windows: scoop install doctl"
    echo -e "Or visit: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if authenticated with DigitalOcean
echo -e "${YELLOW}Verifying DigitalOcean authentication...${NC}"
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Not authenticated with DigitalOcean. Please run 'doctl auth init' first.${NC}"
    exit 1
fi

echo -e "${GREEN}Authentication successful!${NC}"

# Verify the project files
echo -e "${YELLOW}Verifying project files...${NC}"

# Check for package.json
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found${NC}"
    exit 1
fi

# Check for next.config.ts
if [ ! -f "next.config.ts" ]; then
    echo -e "${RED}Error: next.config.ts not found${NC}"
    exit 1
fi

# Check for Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found${NC}"
    exit 1
fi

# Check for .do/app.yaml
if [ ! -f ".do/app.yaml" ]; then
    echo -e "${RED}Error: .do/app.yaml not found${NC}"
    exit 1
fi

echo -e "${GREEN}All required files found!${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm install

# Build the application
echo -e "${YELLOW}Building the application...${NC}"
npm run build

echo -e "${GREEN}Build successful!${NC}"

# Check for existing app
echo -e "${YELLOW}Checking if app already exists...${NC}"
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo -e "${YELLOW}No existing app found. Creating a new one...${NC}"
    
    # Create a new app
    echo -e "${YELLOW}Creating new app on DigitalOcean...${NC}"
    doctl apps create --spec .do/app.yaml
    
    # Get the app ID
    APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        echo -e "${RED}Failed to create app. Please check the logs for errors.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}App created successfully with ID: $APP_ID${NC}"
else
    echo -e "${GREEN}Found existing app with ID: $APP_ID${NC}"
    
    # Update the existing app
    echo -e "${YELLOW}Updating existing app on DigitalOcean...${NC}"
    doctl apps update $APP_ID --spec .do/app.yaml
    
    echo -e "${GREEN}App updated successfully!${NC}"
fi

# Get the app URL
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${GREEN}App URL: $APP_URL${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Monitor the deployment
echo -e "${YELLOW}Monitoring deployment...${NC}"
echo -e "${YELLOW}Getting latest deployment ID...${NC}"

DEPLOYMENT_ID=$(doctl apps list-deployments $APP_ID --format ID --no-header | head -n 1)
if [ -n "$DEPLOYMENT_ID" ]; then
    echo -e "${GREEN}Latest deployment ID: $DEPLOYMENT_ID${NC}"
    
    # Get deployment status
    DEPLOYMENT_STATUS=$(doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format Phase --no-header)
    echo -e "${YELLOW}Deployment status: $DEPLOYMENT_STATUS${NC}"
    
    # If you want to wait for the deployment to complete, uncomment the following block
    echo -e "${YELLOW}Waiting for deployment to complete...${NC}"
    while [ "$DEPLOYMENT_STATUS" != "ACTIVE" ] && [ "$DEPLOYMENT_STATUS" != "ERROR" ]; do
        echo -e "${YELLOW}Current status: $DEPLOYMENT_STATUS. Waiting 30 seconds...${NC}"
        sleep 30
        DEPLOYMENT_STATUS=$(doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format Phase --no-header)
    done
    
    if [ "$DEPLOYMENT_STATUS" == "ACTIVE" ]; then
        echo -e "${GREEN}Deployment completed successfully!${NC}"
    else
        echo -e "${RED}Deployment failed with status: $DEPLOYMENT_STATUS${NC}"
        echo -e "${YELLOW}Checking deployment logs...${NC}"
        doctl apps logs $APP_ID --deployment $DEPLOYMENT_ID
    fi
else
    echo -e "${RED}Could not get deployment ID. Please check manually.${NC}"
fi

# Output commands for further monitoring
echo -e "\n${YELLOW}To check deployment status:${NC}"
echo -e "${GREEN}doctl apps get-deployment $APP_ID $DEPLOYMENT_ID${NC}"

echo -e "\n${YELLOW}To view logs:${NC}"
echo -e "${GREEN}doctl apps logs $APP_ID${NC}"

echo -e "\n${YELLOW}To follow logs in real-time:${NC}"
echo -e "${GREEN}doctl apps logs $APP_ID --follow${NC}"

echo -e "\n${YELLOW}To run the monitoring script:${NC}"
echo -e "${GREEN}node scripts/monitoring-script.js $APP_ID${NC}"

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}DigitalOcean deployment process completed!${NC}"
echo -e "${BLUE}=========================================================${NC}"
