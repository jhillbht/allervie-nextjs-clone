#!/bin/bash
# Allervie Analytics Dashboard Deployment Script

set -e # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Analytics Dashboard Deployment Script        ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Verify doctl is installed
echo -e "${YELLOW}Checking if doctl is installed...${NC}"
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}doctl is not installed. Please install it first.${NC}"
    echo "Visit https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Verify doctl authentication
echo -e "${YELLOW}Verifying DigitalOcean authentication...${NC}"
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Not authenticated with DigitalOcean. Please run 'doctl auth init' first.${NC}"
    exit 1
fi

echo -e "${GREEN}Authentication successful!${NC}"

# Update the app in DigitalOcean
echo -e "${YELLOW}Checking for existing app...${NC}"
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "allervie-analytics-dashboard" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo -e "${YELLOW}Creating new app...${NC}"
    doctl apps create --spec .do/app.yaml
else
    echo -e "${YELLOW}Updating existing app (ID: $APP_ID)...${NC}"
    doctl apps update $APP_ID --spec .do/app.yaml
fi

echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${YELLOW}App ID: $APP_ID${NC}"

# Get deployment ID
echo -e "${YELLOW}Getting latest deployment ID...${NC}"
DEPLOYMENT_ID=$(doctl apps list-deployments $APP_ID --format ID --no-header | head -n 1)

if [ -n "$DEPLOYMENT_ID" ]; then
    echo -e "${YELLOW}Deployment ID: $DEPLOYMENT_ID${NC}"
    echo -e "${YELLOW}To view deployment logs, run:${NC}"
    echo -e "doctl apps logs $APP_ID"
    echo -e "${GREEN}Deployment initiated. Use the monitor.sh script to check status.${NC}"
else
    echo -e "${RED}Failed to get deployment ID. Please check manually with 'doctl apps list-deployments $APP_ID'.${NC}"
fi
