#!/bin/bash
# Fix build command for pnpm in app.yaml
# This script updates the build_command in app.yaml to be compatible with pnpm

set -e # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Fix build_command for pnpm                           ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Variables
REPO_PATH="/Users/supabowl/Downloads/Cursor/allervie-nextjs-clone"
APP_YAML_PATH="${REPO_PATH}/.do/app.yaml"

# Change to repository directory
echo -e "${YELLOW}Changing to repository directory: $REPO_PATH${NC}"
cd "$REPO_PATH" || { echo -e "${RED}Error: Could not change to repository directory${NC}"; exit 1; }

# Verify app.yaml exists
if [ ! -f "$APP_YAML_PATH" ]; then
    echo -e "${RED}Error: app.yaml not found at $APP_YAML_PATH${NC}"
    exit 1
fi

# Update the build_command in app.yaml
echo -e "${YELLOW}Updating build_command in app.yaml...${NC}"
sed -i.bak 's/build_command: npm ci && npm run build/build_command: pnpm install --frozen-lockfile && pnpm build/g' "$APP_YAML_PATH"
rm "${APP_YAML_PATH}.bak"

# Check if the replacement was successful
if grep -q "build_command: pnpm install --frozen-lockfile && pnpm build" "$APP_YAML_PATH"; then
    echo -e "${GREEN}Successfully updated build_command in app.yaml!${NC}"
else
    echo -e "${RED}Failed to update build_command in app.yaml.${NC}"
    exit 1
fi

# Verify updated app.yaml
echo -e "${YELLOW}Updated app.yaml content:${NC}"
cat "$APP_YAML_PATH"

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git add "$APP_YAML_PATH"
git commit -m "Fix: Update build_command to use pnpm with frozen lockfile" || true

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}Build command fix applied!${NC}"
echo -e "${YELLOW}To deploy the updated configuration, run:${NC}"
echo -e "${GREEN}./deploy-digitalocean.sh${NC}"
echo -e "${BLUE}=========================================================${NC}"
