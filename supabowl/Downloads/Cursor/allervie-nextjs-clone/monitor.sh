#!/bin/bash
# Script to monitor deployment status

APP_ID="2ec0029a-7736-41ce-bb63-d7c3e8642c7c"
DEPLOYMENT_ID="19602b18-10ab-4f36-be50-4347fee062c0"

# Loop to check status every 30 seconds
while true; do
  # Get deployment status
  DEPLOYMENT_STATUS=$(doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format Phase --no-header)
  TIMESTAMP=$(date +"%T")
  
  echo "[$TIMESTAMP] Deployment status: $DEPLOYMENT_STATUS"
  
  # Check if deployment is complete
  if [ "$DEPLOYMENT_STATUS" == "ACTIVE" ]; then
    echo "Deployment completed successfully!"
    break
  elif [ "$DEPLOYMENT_STATUS" == "ERROR" ]; then
    echo "Deployment failed with status: $DEPLOYMENT_STATUS"
    doctl apps get-deployment $APP_ID $DEPLOYMENT_ID -o json
    break
  fi
  
  # Wait 30 seconds before checking again
  sleep 30
done