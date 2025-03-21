#!/bin/bash
# Allervie Analytics Dashboard DigitalOcean Deployment Script

set -e # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Analytics Dashboard Deployment Script        ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Check if doctl is installed
echo -e "${YELLOW}Checking if doctl is installed...${NC}"
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}doctl is not installed. Please install it first.${NC}"
    echo "Visit https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if authenticated
echo -e "${YELLOW}Checking if authenticated with DigitalOcean...${NC}"
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Not authenticated with DigitalOcean. Please run 'doctl auth init' first.${NC}"
    exit 1
fi

echo -e "${GREEN}Authenticated with DigitalOcean!${NC}"

# Prepare for deployment
echo -e "${YELLOW}Preparing for deployment...${NC}"

# Check for existing app
APP_NAME="allervie-analytics-dashboard"
echo -e "${YELLOW}Checking if app already exists...${NC}"
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')

# Deploy to DigitalOcean
echo -e "${YELLOW}Deploying to DigitalOcean App Platform...${NC}"

if [ -z "$APP_ID" ]; then
    echo -e "${YELLOW}Creating new app...${NC}"
    doctl apps create --spec .do/app.yaml
else
    echo -e "${YELLOW}Updating existing app (ID: $APP_ID)...${NC}"
    doctl apps update $APP_ID --spec .do/app.yaml
fi

# Get app details
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -n "$APP_ID" ]; then
    echo -e "${GREEN}App ID: $APP_ID${NC}"
    
    # Get app URL
    APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)
    echo -e "${GREEN}App URL: $APP_URL${NC}"
    
    # Get deployment info
    DEPLOYMENT_ID=$(doctl apps list-deployments $APP_ID --format ID --no-header | head -n 1)
    if [ -n "$DEPLOYMENT_ID" ]; then
        echo -e "${YELLOW}Latest deployment: $DEPLOYMENT_ID${NC}"
        doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format "Phase,Progress,Created"
    fi
    
    echo -e "${BLUE}=========================================================${NC}"
    echo -e "${GREEN}Deployment initiated successfully!${NC}"
    echo -e "${YELLOW}To monitor the deployment, run:${NC}"
    echo -e "doctl apps logs $APP_ID --follow"
    echo -e "${BLUE}=========================================================${NC}"
else
    echo -e "${RED}Failed to get app ID. Please check the logs for errors.${NC}"
fi
