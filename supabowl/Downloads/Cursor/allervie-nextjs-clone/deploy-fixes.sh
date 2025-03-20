#!/bin/bash
# Script to deploy the fixed Allervie Dashboard to DigitalOcean App Platform

set -e # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Dashboard Deployment Fix Script              ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Change to the repository directory
cd "$(dirname "$0")" || { echo -e "${RED}Error: Could not change to script directory${NC}"; exit 1; }

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}doctl is not installed. Please install it first.${NC}"
    echo -e "Visit https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if authenticated with DigitalOcean
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Not authenticated with DigitalOcean. Please run 'doctl auth init' first.${NC}"
    exit 1
fi

echo -e "${GREEN}Authentication successful!${NC}"

# Check for existing app
APP_NAME="allervie-analytics-dashboard"
echo -e "${YELLOW}Checking for existing app...${NC}"
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo -e "${RED}No app found with name: $APP_NAME${NC}"
    echo -e "${YELLOW}Creating a new app...${NC}"
    doctl apps create --spec .do/app.yaml
    
    # Get the new app ID
    APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        echo -e "${RED}Failed to create app. Please check the logs for errors.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Found existing app with ID: $APP_ID${NC}"
    
    # Update existing app
    echo -e "${YELLOW}Updating app with the new configuration...${NC}"
    doctl apps update $APP_ID --spec .do/app.yaml
fi

# Get the app URL
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${GREEN}App URL: $APP_URL${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Monitor the deployment
echo -e "${YELLOW}Monitoring deployment...${NC}"
DEPLOYMENT_ID=$(doctl apps list-deployments $APP_ID --format ID --no-header | head -n 1)

if [ -n "$DEPLOYMENT_ID" ]; then
    echo -e "${GREEN}Latest deployment ID: $DEPLOYMENT_ID${NC}"
    
    # Display initial status
    DEPLOYMENT_STATUS=$(doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format Phase --no-header)
    echo -e "${YELLOW}Initial deployment status: $DEPLOYMENT_STATUS${NC}"
    
    # Wait for deployment to complete
    echo -e "${YELLOW}Waiting for deployment to complete...${NC}"
    echo -e "${YELLOW}This may take a few minutes...${NC}"
    
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
    
    # Output commands for further monitoring
    echo -e "\n${YELLOW}To check deployment status:${NC}"
    echo -e "${GREEN}doctl apps get-deployment $APP_ID $DEPLOYMENT_ID${NC}"
    
    echo -e "\n${YELLOW}To view logs:${NC}"
    echo -e "${GREEN}doctl apps logs $APP_ID${NC}"
    
    echo -e "\n${YELLOW}To follow logs in real-time:${NC}"
    echo -e "${GREEN}doctl apps logs $APP_ID --follow${NC}"
else
    echo -e "${RED}Could not get deployment ID. Please check manually.${NC}"
fi

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}Deployment process completed!${NC}"
echo -e "${BLUE}=========================================================${NC}"