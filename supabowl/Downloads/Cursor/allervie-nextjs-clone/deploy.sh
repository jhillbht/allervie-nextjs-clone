#!/bin/bash
# Simple deployment script for Allervie Analytics Dashboard

set -e # Exit on any error

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
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}doctl is not installed. Please install it first.${NC}"
    echo "Visit https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if authenticated
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Not authenticated with DigitalOcean. Please run 'doctl auth init' first.${NC}"
    exit 1
fi

echo -e "${GREEN}Authenticated with DigitalOcean!${NC}"

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

echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${YELLOW}To monitor the deployment, use:${NC}"
echo -e "doctl apps list-deployments $APP_ID"
