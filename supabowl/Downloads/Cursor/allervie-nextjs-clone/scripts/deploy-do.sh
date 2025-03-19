#!/bin/bash
# Improved DigitalOcean Deployment Script for Allervie Dashboard

set -e # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Dashboard Deployment to DigitalOcean        ${NC}"
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

# Create or update the app
echo -e "\n${YELLOW}Deploying application to DigitalOcean App Platform...${NC}"

# Get the app.yaml path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_YAML_PATH="$SCRIPT_DIR/../.do/app.yaml"

# Check if the app.yaml exists
if [ ! -f "$APP_YAML_PATH" ]; then
    echo -e "${RED}app.yaml not found at $APP_YAML_PATH${NC}"
    exit 1
fi

# Check if the app already exists
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "allervie-nextjs-dashboard" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo -e "${YELLOW}Creating new DigitalOcean App...${NC}"
    DEPLOYMENT_OUTPUT=$(doctl apps create --spec "$APP_YAML_PATH" --format ID --no-header)
    APP_ID=$DEPLOYMENT_OUTPUT
    echo -e "${GREEN}App created with ID: $APP_ID${NC}"
else
    echo -e "${YELLOW}Updating existing DigitalOcean App (ID: $APP_ID)...${NC}"
    doctl apps update "$APP_ID" --spec "$APP_YAML_PATH"
    echo -e "${GREEN}App update initiated!${NC}"
fi

echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${YELLOW}Monitoring deployment progress...${NC}"

# Function to get deployment ID of the latest deployment
get_latest_deployment_id() {
    doctl apps list-deployments "$APP_ID" --format ID --no-header | head -n 1
}

# Function to get deployment status
get_deployment_status() {
    local deployment_id=$1
    doctl apps get-deployment "$APP_ID" "$deployment_id" --format Phase --no-header
}

# Wait for the deployment to complete
DEPLOYMENT_ID=$(get_latest_deployment_id)
echo -e "${YELLOW}Deployment ID: $DEPLOYMENT_ID${NC}"

# Display initial status
STATUS=$(get_deployment_status "$DEPLOYMENT_ID")
echo -e "${YELLOW}Initial status: $STATUS${NC}"

# Poll for status changes
echo -e "${YELLOW}Waiting for deployment to complete...${NC}"
while [ "$STATUS" == "PENDING" ] || [ "$STATUS" == "BUILDING" ] || [ "$STATUS" == "DEPLOYING" ]; do
    echo -e "${YELLOW}Current status: $STATUS${NC}"
    sleep 10
    STATUS=$(get_deployment_status "$DEPLOYMENT_ID")
done

# Get app details
APP_URL=$(doctl apps get "$APP_ID" --format "DefaultIngress" --no-header)

# Check final status
if [ "$STATUS" == "ACTIVE" ]; then
    echo -e "\n${GREEN}==================================================${NC}"
    echo -e "${GREEN}    Deployment Successful!                         ${NC}"
    echo -e "${GREEN}==================================================${NC}"
    echo -e "${GREEN}Application URL: $APP_URL${NC}"
    echo -e "${GREEN}App ID: $APP_ID${NC}"
    echo -e "${GREEN}Deployment ID: $DEPLOYMENT_ID${NC}"
    echo -e "${YELLOW}Note: It may take a few more minutes for the application to be fully available.${NC}"
else
    echo -e "\n${RED}==================================================${NC}"
    echo -e "${RED}    Deployment failed with status: $STATUS          ${NC}"
    echo -e "${RED}==================================================${NC}"
    echo -e "${YELLOW}Fetching logs for troubleshooting...${NC}"
    
    echo -e "\n${YELLOW}Web component logs:${NC}"
    doctl apps logs "$APP_ID" --component web --follow false --tail 50
    
    echo -e "\n${YELLOW}API component logs:${NC}"
    doctl apps logs "$APP_ID" --component api --follow false --tail 50
    
    echo -e "\n${RED}Deployment failed. See logs above for details.${NC}"
    echo -e "${YELLOW}You can get more logs with: doctl apps logs $APP_ID --component [web|api]${NC}"
fi

echo -e "\n${BLUE}=========================================================${NC}"
echo -e "${BLUE}                 Deployment Complete                      ${NC}"
echo -e "${BLUE}=========================================================${NC}"
