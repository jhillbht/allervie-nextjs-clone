#!/bin/bash
set -e

echo "Deploying Allervie Analytics Dashboard to DigitalOcean..."

# Check if doctl is authenticated
if ! doctl account get >/dev/null 2>&1; then
  echo "Error: doctl not authenticated. Please run 'doctl auth init' first."
  exit 1
fi

# Find the app ID by name
APP_NAME="allervie-analytics-dashboard"
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
  echo "Creating new app from app.yaml..."
  doctl apps create --spec app.yaml --wait
  APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')
else
  echo "Updating existing app with ID: $APP_ID"
  doctl apps update $APP_ID --spec app.yaml --wait
fi

echo "Deployment initiated! App URL:"
doctl apps get $APP_ID --format DefaultIngress --no-header

echo ""
echo "Deployment in progress. You can check status with:"
echo "doctl apps get $APP_ID"
echo ""
echo "To view logs:"
echo "doctl apps logs $APP_ID"
echo ""
echo "When deployment is complete, access the dashboard at:"
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)
echo "https://$APP_URL/ads-dashboard"