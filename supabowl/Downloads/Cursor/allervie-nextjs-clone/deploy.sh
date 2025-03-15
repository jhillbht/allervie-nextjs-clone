#!/bin/bash

# Exit on error
set -e

echo "=== Allervie Dashboard Deployment Script ==="
echo "This script will deploy the Allervie Dashboard to DigitalOcean App Platform."

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl is not installed. Please install it first:"
    echo "For macOS: brew install doctl"
    echo "For more installation options, visit: https://github.com/digitalocean/doctl#installing-doctl"
    exit 1
fi

# Check if user is authenticated with DigitalOcean
if ! doctl account get &> /dev/null; then
    echo "You need to authenticate with DigitalOcean first."
    echo "Please run: doctl auth init"
    echo "Then try again."
    exit 1
fi

echo "=== Building the Next.js application ==="
npm run build

echo "=== Creating/Updating App on DigitalOcean ==="
# Check if APP_ID environment variable exists
if [ -z "$DO_APP_ID" ]; then
    echo "Creating new app on DigitalOcean App Platform..."
    APP_INFO=$(doctl apps create --spec .do/app.yaml --format ID --no-header)
    APP_ID=$(echo $APP_INFO | awk '{print $1}')
    echo "Created new app with ID: $APP_ID"
    echo "You may want to save this ID as DO_APP_ID in your environment variables."
else
    echo "Updating existing app with ID: $DO_APP_ID"
    doctl apps update $DO_APP_ID --spec .do/app.yaml
    APP_ID=$DO_APP_ID
fi

echo "=== Triggering Deployment ==="
DEPLOYMENT_ID=$(doctl apps create-deployment $APP_ID --format ID --no-header)
echo "Deployment initiated with ID: $DEPLOYMENT_ID"

echo "=== Waiting for Deployment to Complete ==="
echo "This may take several minutes..."

while true; do
    DEPLOYMENT_STATUS=$(doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format Phase --no-header)
    echo -n "."
    
    if [ "$DEPLOYMENT_STATUS" == "ACTIVE" ]; then
        echo -e "\nDeployment completed successfully!"
        break
    elif [ "$DEPLOYMENT_STATUS" == "ERROR" ] || [ "$DEPLOYMENT_STATUS" == "FAILED" ]; then
        echo -e "\nDeployment failed. Check logs for details:"
        echo "doctl apps logs $APP_ID --deployment $DEPLOYMENT_ID"
        exit 1
    fi
    
    sleep 10
done

# Get the app URL
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)
echo "=== Deployment Complete ==="
echo "Your application is now available at: $APP_URL"
echo "To view logs: doctl apps logs $APP_ID"
echo "To view active deployment: doctl apps get-deployment $APP_ID $DEPLOYMENT_ID"
