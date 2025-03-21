#!/bin/bash
# Allervie Analytics Dashboard Deployment Monitoring Script

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Analytics Dashboard Deployment Monitor       ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Get the app ID
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "allervie-analytics-dashboard" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo -e "${RED}Could not find Allervie Analytics Dashboard app.${NC}"
    exit 1
fi

echo -e "${YELLOW}Found app with ID: $APP_ID${NC}"

# Get app info
echo -e "${YELLOW}Getting app details...${NC}"
APP_INFO=$(doctl apps get $APP_ID --format "Spec.Name,DefaultIngress")
APP_NAME=$(echo "$APP_INFO" | awk '{print $1}')
APP_URL=$(echo "$APP_INFO" | awk '{print $2}')

echo -e "${GREEN}App Name: $APP_NAME${NC}"
echo -e "${GREEN}App URL: $APP_URL${NC}"

# Get latest deployment
echo -e "${YELLOW}Getting deployment details...${NC}"
DEPLOYMENT_ID=$(doctl apps list-deployments $APP_ID --format ID --no-header | head -n 1)

if [ -n "$DEPLOYMENT_ID" ]; then
    echo -e "${GREEN}Latest Deployment ID: $DEPLOYMENT_ID${NC}"
    
    # Get deployment details
    DEPLOYMENT_INFO=$(doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format "Phase,Progress")
    DEPLOYMENT_PHASE=$(echo "$DEPLOYMENT_INFO" | awk '{print $1}')
    DEPLOYMENT_PROGRESS=$(echo "$DEPLOYMENT_INFO" | awk '{print $2}')
    
    # Display deployment status with color
    case "$DEPLOYMENT_PHASE" in
        "PENDING" | "BUILDING" | "DEPLOYING")
            echo -e "${YELLOW}Deployment Status: $DEPLOYMENT_PHASE ${DEPLOYMENT_PROGRESS}${NC}"
            ;;
        "ACTIVE" | "DEPLOYED")
            echo -e "${GREEN}Deployment Status: $DEPLOYMENT_PHASE${NC}"
            ;;
        "ERROR" | "FAILED")
            echo -e "${RED}Deployment Status: $DEPLOYMENT_PHASE${NC}"
            ;;
        *)
            echo -e "Deployment Status: $DEPLOYMENT_PHASE"
            ;;
    esac
else
    echo -e "${RED}No deployments found.${NC}"
fi

# Show recent logs
echo -e "\n${YELLOW}Recent Logs:${NC}"
doctl apps logs $APP_ID --tail 20

# Provide command to follow logs
echo -e "\n${YELLOW}To follow logs in real-time, run:${NC}"
echo -e "doctl apps logs $APP_ID --follow"

# If app URL is available and deployment is active, check health endpoint
if [ -n "$APP_URL" ] && [ "$DEPLOYMENT_PHASE" == "ACTIVE" ]; then
    echo -e "\n${YELLOW}Checking health endpoint...${NC}"
    HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/api/health")
    
    if [ "$HEALTH_CODE" == "200" ]; then
        echo -e "${GREEN}Health check passed: 200 OK${NC}"
        
        # Get health details
        HEALTH_DETAILS=$(curl -s "$APP_URL/api/health")
        echo -e "Health Details: $HEALTH_DETAILS"
    else
        echo -e "${RED}Health check failed: $HEALTH_CODE${NC}"
    fi
fi
