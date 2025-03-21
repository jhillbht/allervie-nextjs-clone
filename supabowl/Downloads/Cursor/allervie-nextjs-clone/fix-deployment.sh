#!/bin/bash
# Allervie Dashboard Deployment Fix Script
# This script identifies and fixes issues with the DigitalOcean App Platform deployment

set -e # Exit on any error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Allervie Dashboard Deployment Fix Script              ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Variables - Update these with your information
REPO_PATH="/Users/supabowl/Downloads/Cursor/allervie-nextjs-clone"
APP_NAME="allervie-analytics-dashboard"

# Change to repository directory
echo -e "${YELLOW}Changing to repository directory: $REPO_PATH${NC}"
cd "$REPO_PATH" || { echo -e "${RED}Error: Could not change to repository directory${NC}"; exit 1; }

# Check if package-lock.json exists and remove pnpm-lock.yaml if it exists
if [ -f "package-lock.json" ]; then
    echo -e "${YELLOW}Found package-lock.json, ensuring we're using npm...${NC}"
    
    # Remove pnpm-lock.yaml if it exists
    if [ -f "pnpm-lock.yaml" ]; then
        echo -e "${YELLOW}Removing pnpm-lock.yaml...${NC}"
        rm pnpm-lock.yaml
    fi
    
    # Update package.json to ensure correct packageManager field
    echo -e "${YELLOW}Updating package.json packageManager field...${NC}"
    sed -i.bak '/packageManager/d' package.json
    rm package.json.bak
    
    echo -e "${GREEN}Project configured to use npm!${NC}"
else
    echo -e "${YELLOW}package-lock.json not found, using npm to generate it...${NC}"
    # Install dependencies with npm to generate package-lock.json
    npm install
    
    # Remove pnpm-lock.yaml if it exists
    if [ -f "pnpm-lock.yaml" ]; then
        echo -e "${YELLOW}Removing pnpm-lock.yaml...${NC}"
        rm pnpm-lock.yaml
    fi
    
    echo -e "${GREEN}Package configuration updated!${NC}"
fi

# Update next.config.js to ensure correct configuration
echo -e "${YELLOW}Updating next.config.js...${NC}"
cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  reactStrictMode: true,
  env: {
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
    GOOGLE_ADS_DEVELOPER_TOKEN: process.env.GOOGLE_ADS_DEVELOPER_TOKEN,
    GOOGLE_ADS_LOGIN_CUSTOMER_ID: process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
    GOOGLE_ADS_CUSTOMER_ID: process.env.GOOGLE_ADS_CUSTOMER_ID,
    GOOGLE_ADS_REFRESH_TOKEN: process.env.GOOGLE_ADS_REFRESH_TOKEN,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
EOF

echo -e "${GREEN}next.config.js updated!${NC}"

# Update the Dockerfile to use the correct Node.js version
echo -e "${YELLOW}Updating Dockerfile...${NC}"
cat > Dockerfile << 'EOF'
FROM node:22-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Environment variables must be present at build time
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

# Build Next.js
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 8080

# Environment variables
ENV PORT 8080
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/api/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF

echo -e "${GREEN}Dockerfile updated!${NC}"

# Update .do/app.yaml for DigitalOcean deployment
echo -e "${YELLOW}Updating app.yaml...${NC}"
mkdir -p .do
cat > .do/app.yaml << EOF
name: allervie-analytics-dashboard
region: sfo
services:
  - name: nextjs-dashboard
    github:
      repo: jhillbht/allervie-nextjs-clone
      branch: main
      deploy_on_push: true
    build_command: npm ci && npm run build
    run_command: npm start
    http_port: 8080
    instance_count: 1
    instance_size_slug: basic-xs
    routes:
      - path: /
        preserve_path_prefix: false
    health_check:
      http_path: /api/health
      initial_delay_seconds: 20
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3
    envs:
      # Authentication variables
      - key: NEXTAUTH_URL
        scope: RUN_AND_BUILD_TIME
        value: \${APP_URL}
      - key: NEXTAUTH_SECRET
        scope: RUN_AND_BUILD_TIME
        type: SECRET
        value: allervie-dashboard-next-secret-key-2025
      
      # Google API credentials
      - key: GOOGLE_CLIENT_ID
        scope: RUN_AND_BUILD_TIME
        value: 22083613754-d1omeg2958vrsndpqg2v1jp0ncm7sr23.apps.googleusercontent.com
      - key: GOOGLE_CLIENT_SECRET
        scope: RUN_AND_BUILD_TIME
        type: SECRET
        value: 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
      
      # Google Ads API credentials
      - key: GOOGLE_ADS_DEVELOPER_TOKEN
        scope: RUN_AND_BUILD_TIME
        type: SECRET
        value: kqcdDd6o0AAACpgKAZIRHw # Replace with actual token
      - key: GOOGLE_ADS_LOGIN_CUSTOMER_ID
        scope: RUN_AND_BUILD_TIME
        value: "8127539892" # Replace with actual ID
      - key: GOOGLE_ADS_CUSTOMER_ID 
        scope: RUN_AND_BUILD_TIME
        value: "8127539892" # Replace with actual ID
      - key: GOOGLE_ADS_REFRESH_TOKEN
        scope: RUN_AND_BUILD_TIME
        type: SECRET
        value: "1//06rKB7BnQZXNwCgYIARAAGAYSNwF-L9IrLOnYbRX-mNOWeFxpGdNnV46RfDIUvO7F0xHy5c_gLKAHNH6xOm0UuGXsYRPajjRDGBE" # Replace with actual token
      
      # Application configuration
      - key: NODE_ENV
        scope: RUN_AND_BUILD_TIME
        value: production
      - key: NEXT_PUBLIC_API_URL
        scope: RUN_AND_BUILD_TIME
        value: \${APP_URL}/api
      
      # Performance and monitoring
      - key: NEXT_TELEMETRY_DISABLED
        scope: RUN_AND_BUILD_TIME
        value: "1"
EOF

echo -e "${GREEN}app.yaml updated!${NC}"

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git add next.config.js Dockerfile .do/app.yaml
git commit -m "Fix: Update configuration for DigitalOcean App Platform deployment" || true

echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}All fixes have been applied!${NC}"
echo -e "${YELLOW}To deploy to DigitalOcean App Platform, run:${NC}"
echo -e "${GREEN}./deploy-digitalocean.sh${NC}"
echo -e "${BLUE}=========================================================${NC}"
