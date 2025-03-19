#!/bin/bash
# Script to update environment variables and deploy Allervie Dashboard to DigitalOcean

set -e # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Dashboard Environment Update & Deployment    ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Configuration - update these values
APP_ID="a4374fbe-a0eb-49f5-a1c3-b55e70f8e5ec" # Update with your actual app ID
GOOGLE_CLIENT_ID="your-google-client-id" # Update with your actual client ID
GOOGLE_CLIENT_SECRET="your-google-client-secret" # Update with your actual client secret
OAUTH_REDIRECT_URI="https://allervie-unified-fsx78.ondigitalocean.app/api/auth/callback"

# Check if doctl is installed
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

# Get current app spec
echo -e "${YELLOW}Downloading current app specification...${NC}"
doctl apps get $APP_ID --format spec > app-spec.yaml

if [ ! -f app-spec.yaml ]; then
    echo -e "${RED}Error: Failed to download app specification.${NC}"
    exit 1
fi

# Create a backup of the original spec
cp app-spec.yaml app-spec.yaml.bak

echo -e "${YELLOW}Updating environment variables...${NC}"

# Process the YAML to add/update environment variables
echo -e "${YELLOW}Adding/updating OAuth environment variables...${NC}"

# Check if yq is installed (for easier YAML manipulation)
if command -v yq &> /dev/null; then
    echo -e "${GREEN}Using yq for YAML manipulation${NC}"
    
    # Find the web service and update/add environment variables using yq
    # This is a more robust approach than using sed
    SERVICE_INDEX=$(yq e '.services | map(.name == "web") | index(true)' app-spec.yaml)
    
    if [ "$SERVICE_INDEX" != "null" ]; then
        # Add/update GOOGLE_CLIENT_ID
        yq e ".services[$SERVICE_INDEX].envs += [{\"key\": \"GOOGLE_CLIENT_ID\", \"value\": \"$GOOGLE_CLIENT_ID\", \"scope\": \"RUN_AND_BUILD_TIME\"}]" -i app-spec.yaml
        
        # Add/update GOOGLE_CLIENT_SECRET
        yq e ".services[$SERVICE_INDEX].envs += [{\"key\": \"GOOGLE_CLIENT_SECRET\", \"value\": \"$GOOGLE_CLIENT_SECRET\", \"type\": \"SECRET\", \"scope\": \"RUN_AND_BUILD_TIME\"}]" -i app-spec.yaml
        
        # Add/update OAUTH_REDIRECT_URI
        yq e ".services[$SERVICE_INDEX].envs += [{\"key\": \"OAUTH_REDIRECT_URI\", \"value\": \"$OAUTH_REDIRECT_URI\", \"scope\": \"RUN_AND_BUILD_TIME\"}]" -i app-spec.yaml
        
        echo -e "${GREEN}Environment variables added/updated successfully with yq${NC}"
    else
        echo -e "${RED}Could not find web service in app spec${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}yq not found, using sed for YAML manipulation${NC}"
    echo -e "${YELLOW}This method is less robust and may require manual verification${NC}"
    
    # Function to check if an env var exists in the spec
    env_var_exists() {
        local key=$1
        grep -q "key: $key" app-spec.yaml
        return $?
    }
    
    # Function to update or add an env var
    # This is a simplified approach and might need adjustments
    update_env_var() {
        local key=$1
        local value=$2
        local is_secret=$3
        
        # Check if key exists
        if env_var_exists $key; then
            # Update existing key
            echo -e "  ${YELLOW}Updating existing environment variable: $key${NC}"
            # This is a simple approach using sed - might need adjustment
            if [ "$is_secret" = true ]; then
                sed -i "/key: $key/,/scope:/s/value:.*/value: $value\n        type: SECRET/" app-spec.yaml
            else
                sed -i "/key: $key/,/scope:/s/value:.*/value: $value/" app-spec.yaml
            fi
        else
            # Add new key - find the web service and add env var
            echo -e "  ${YELLOW}Adding new environment variable: $key${NC}"
            # Find the first 'envs:' section after 'name: web'
            if [ "$is_secret" = true ]; then
                sed -i "/name: web/,/envs:/s/envs:/envs:\n      - key: $key\n        value: $value\n        type: SECRET\n        scope: RUN_AND_BUILD_TIME/" app-spec.yaml
            else
                sed -i "/name: web/,/envs:/s/envs:/envs:\n      - key: $key\n        value: $value\n        scope: RUN_AND_BUILD_TIME/" app-spec.yaml
            fi
        fi
    }
    
    # Update environment variables
    update_env_var "GOOGLE_CLIENT_ID" "$GOOGLE_CLIENT_ID" false
    update_env_var "GOOGLE_CLIENT_SECRET" "$GOOGLE_CLIENT_SECRET" true
    update_env_var "OAUTH_REDIRECT_URI" "$OAUTH_REDIRECT_URI" false
fi

# Display the changes for verification
echo -e "${YELLOW}Here's