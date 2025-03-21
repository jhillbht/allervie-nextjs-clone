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

# Get deployment details
echo -e "${YELLOW}Getting deployment details...${NC}"
APP_DETAILS=$(doctl apps get $APP_ID --format "Spec.Name,DefaultIngress,ActiveDeployment.ID,ActiveDeployment.Phase,ActiveDeployment.Progress.SuccessSteps,ActiveDeployment.Progress.TotalSteps,ActiveDeployment.Progress.ErrorSteps")

APP_NAME=$(echo "$APP_DETAILS" | awk '{print $1}')
APP_URL=$(echo "$APP_DETAILS" | awk '{print $2}')
DEPLOYMENT_ID=$(echo "$APP_DETAILS" | awk '{print $3}')
DEPLOYMENT_PHASE=$(echo "$APP_DETAILS" | awk '{print $4}')
SUCCESS_STEPS=$(echo "$APP_DETAILS" | awk '{print $5}')
TOTAL_STEPS=$(echo "$APP_DETAILS" | awk '{print $6}')
ERROR_STEPS=$(echo "$APP_DETAILS" | awk '{print $7}')

# Calculate progress percentage
if [ -n "$TOTAL_STEPS" ] && [ "$TOTAL_STEPS" -gt 0 ]; then
    PROGRESS_PCT=$((SUCCESS_STEPS * 100 / TOTAL_STEPS))
else
    PROGRESS_PCT=0
fi

# Display deployment details
echo -e "${GREEN}App Name: $APP_NAME${NC}"
echo -e "${GREEN}App URL: $APP_URL${NC}"
echo -e "${GREEN}Deployment ID: $DEPLOYMENT_ID${NC}"

# Display deployment phase with color
case "$DEPLOYMENT_PHASE" in
    "PENDING" | "BUILDING" | "DEPLOYING")
        echo -e "${YELLOW}Deployment Phase: $DEPLOYMENT_PHASE${NC}"
        ;;
    "ACTIVE" | "DEPLOYED")
        echo -e "${GREEN}Deployment Phase: $DEPLOYMENT_PHASE${NC}"
        ;;
    "ERROR" | "FAILED")
        echo -e "${RED}Deployment Phase: $DEPLOYMENT_PHASE${NC}"
        ;;
    *)
        echo -e "Deployment Phase: $DEPLOYMENT_PHASE"
        ;;
esac

echo -e "Progress: $PROGRESS_PCT% ($SUCCESS_STEPS/$TOTAL_STEPS steps complete)"

if [ -n "$ERROR_STEPS" ] && [ "$ERROR_STEPS" -gt 0 ]; then
    echo -e "${RED}Error Steps: $ERROR_STEPS${NC}"
fi

# Show recent logs
echo -e "\n${YELLOW}Recent Logs:${NC}"
doctl apps logs $APP_ID --tail 25

# Provide command to follow logs
echo -e "\n${YELLOW}To follow logs in real-time, run:${NC}"
echo -e "doctl apps logs $APP_ID --follow"

# If deployment is active, check health endpoint
if [ "$DEPLOYMENT_PHASE" == "ACTIVE" ] && [ -n "$APP_URL" ]; then
    echo -e "\n${YELLOW}Checking health endpoint...${NC}"
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/api/health")
    
    if [ "$HEALTH_CHECK" == "200" ]; then
        echo -e "${GREEN}Health check passed: 200 OK${NC}"
    else
        echo -e "${RED}Health check failed: $HEALTH_CHECK${NC}"
    fi
fi
