#!/bin/bash
set -e

echo "Deploying Allervie Analytics Dashboard to DigitalOcean..."

# Check if doctl is authenticated
if ! doctl account get >/dev/null 2>&1; then
  echo "Error: doctl not authenticated. Please run 'doctl auth init' first."
  exit 1
fi

# Check if we need to commit changes first
if [ -n "$(git status --porcelain)" ]; then
  echo "Uncommitted changes detected."
  echo "Would you like to commit these changes? (y/n)"
  read -r commit_response
  
  if [ "$commit_response" = "y" ]; then
    echo "Enter commit message:"
    read -r commit_message
    
    # Stage and commit changes
    git add .
    git commit -m "$commit_message

    🤖 Generated with [Claude Code](https://claude.ai/code)
    Co-Authored-By: Claude <noreply@anthropic.com>"
    
    # Push changes if a remote branch exists
    if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
      echo "Pushing changes to remote..."
      git push
    else
      echo "No upstream branch set, skipping push."
    fi
  fi
fi

# Find the app ID by name
APP_NAME="allervie-analytics-dashboard"
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')

# Check if we need to update test deployment as well
TEST_APP_NAME="allervie-test-deployment"
TEST_APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$TEST_APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
  echo "Creating new app from app.yaml..."
  doctl apps create --spec app.yaml --wait
  APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')
else
  echo "Updating existing app with ID: $APP_ID"
  doctl apps update $APP_ID --spec app.yaml --wait
fi

# Update test deployment if it exists
if [ -n "$TEST_APP_ID" ]; then
  echo "Updating test deployment with ID: $TEST_APP_ID"
  doctl apps update $TEST_APP_ID --spec app.yaml --wait
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

# After deployment, run health check
echo "Would you like to run a health check after deployment? (y/n)"
read -r health_check_response

if [ "$health_check_response" = "y" ]; then
  echo "Will run health check in 60 seconds to allow deployment to complete..."
  sleep 60
  echo "Running health check..."
  curl -s "https://$APP_URL/api/health" | jq .
  
  echo "Would you like to run the OAuth token verification? (y/n)"
  read -r token_check_response
  
  if [ "$token_check_response" = "y" ]; then
    echo "Running token verification (requires SSH access to app)..."
    doctl apps ssh $APP_ID --command "cd /app && python backend/check_deployment.py"
  fi
fi