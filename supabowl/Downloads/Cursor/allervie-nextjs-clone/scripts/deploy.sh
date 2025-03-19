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

# Pre-flight checks
echo -e "${YELLOW}Running pre-flight checks...${NC}"

# Check if package.json has Node.js version specified
if ! grep -q '"node":' package.json; then
    echo -e "${RED}Node.js version not specified in package.json.${NC}"
    echo -e "${YELLOW}Adding Node.js 22.x to package.json...${NC}"
    # Use temporary file to avoid issues with inline editing
    TMP_FILE=$(mktemp)
    jq '.engines = {"node": "22.x"}' package.json > "$TMP_FILE"
    mv "$TMP_FILE" package.json
fi

# Check if next.config.js has output: 'standalone'
if [ -f "next.config.ts" ] && ! grep -q "output.*standalone" next.config.ts; then
    echo -e "${RED}output: 'standalone' not found in next.config.ts${NC}"
    echo -e "${YELLOW}Please add this configuration for DigitalOcean deployment.${NC}"
    exit 1
fi

# Check for health check endpoint
if [ ! -f "src/app/api/health/route.ts" ] && [ ! -f "pages/api/health.ts" ]; then
    echo -e "${RED}Health check endpoint not found.${NC}"
    echo -e "${YELLOW}Please implement a health check endpoint at /api/health.${NC}"
    exit 1
fi

# Build the application for production
echo -e "${YELLOW}Building the application for production...${NC}"
npm run build

# Deploy to DigitalOcean
echo -e "${YELLOW}Deploying to DigitalOcean App Platform...${NC}"

# Check for existing app
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "allervie-analytics-dashboard" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo -e "${YELLOW}Creating new app...${NC}"
    doctl apps create --spec .do/app.yaml
else
    echo -e "${YELLOW}Updating existing app (ID: $APP_ID)...${NC}"
    doctl apps update $APP_ID --spec .do/app.yaml
fi

echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${YELLOW}Monitoring deployment progress...${NC}"

# Get app details
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "allervie-analytics-dashboard" | awk '{print $1}')

if [ -n "$APP_ID" ]; then
    echo -e "${GREEN}App ID: $APP_ID${NC}"
    
    # Get app URL
    APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)
    echo -e "${GREEN}App URL: $APP_URL${NC}"
    
    echo -e "${BLUE}=========================================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${YELLOW}To monitor your deployment, run:${NC}"
    echo -e "${GREEN}node scripts/monitor-deployment.js $APP_ID${NC}"
    echo -e "${BLUE}=========================================================${NC}"
else
    echo -e "${RED}Failed to get app ID. Please check the logs for errors.${NC}"
fi