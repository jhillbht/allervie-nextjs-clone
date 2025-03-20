# Allervie Dashboard DigitalOcean Deployment Guide

## Overview

This guide outlines the process for deploying the Allervie Dashboard to DigitalOcean App Platform. The dashboard is a Next.js application that visualizes Google Ads API data for marketing teams.

## Prerequisites

Before deploying, ensure you have:

1. **doctl CLI installed**:
   ```bash
   # macOS
   brew install doctl
   
   # Linux
   snap install doctl
   
   # Windows
   scoop install doctl
   ```

2. **DigitalOcean authentication set up**:
   ```bash
   doctl auth init
   ```

3. **GitHub repository** with your code committed and pushed
4. **Google API credentials** for OAuth authentication

## Configuration Files

### 1. `.do/app.yaml`

This file defines the DigitalOcean App Platform configuration:

```yaml
name: allervie-analytics-dashboard
region: sfo
services:
  - name: web
    source_dir: /
    dockerfile_path: Dockerfile
    github:
      repo: jhillbht/allervie-nextjs-clone
      branch: main
      deploy_on_push: true
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
        value: ${APP_URL}
      - key: NEXTAUTH_SECRET
        scope: RUN_AND_BUILD_TIME
        type: SECRET
        value: your-secret-value
      
      # Google API credentials
      - key: GOOGLE_CLIENT_ID
        scope: RUN_AND_BUILD_TIME
        value: your-google-client-id
      - key: GOOGLE_CLIENT_SECRET
        scope: RUN_AND_BUILD_TIME
        type: SECRET
        value: your-google-client-secret
      
      # Application configuration
      - key: NODE_ENV
        scope: RUN_AND_BUILD_TIME
        value: production
      - key: NEXT_PUBLIC_API_URL
        scope: RUN_AND_BUILD_TIME
        value: ${APP_URL}/api
      
      # Performance and monitoring
      - key: NEXT_TELEMETRY_DISABLED
        scope: RUN_AND_BUILD_TIME
        value: "1"
```

### 2. `next.config.ts`

Configure Next.js for production deployment:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',  // Optimize for containerized environments
  poweredByHeader: false, // Remove X-Powered-By header for security
  reactStrictMode: true,
  env: {
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
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
  // API route rewrites
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
```

### 3. `Dockerfile`

```dockerfile
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

# Environment variables
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

# Set proper permissions
RUN mkdir -p .next
RUN chown nextjs:nodejs .next

# Copy necessary files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 8080

# Use 8080 as the standard port for container platforms
ENV PORT 8080
ENV HOSTNAME "0.0.0.0"

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD curl -f http://localhost:8080/api/health || exit 1

CMD ["node", "server.js"]
```

### 4. `package.json`

Ensure these settings are in your package.json:

```json
{
  "engines": {
    "node": "22.x"
  },
  "packageManager": "npm@10.2.3"
}
```

## Deployment Scripts

### 1. Automated Deployment Script (deploy-digitalocean.sh)

```bash
#!/bin/bash
# Allervie Dashboard DigitalOcean Deployment Script

set -e # Exit on any error

# Change to the repository directory
cd "/Users/supabowl/Downloads/Cursor/allervie-nextjs-clone"

# Check prerequisites
if ! command -v doctl &> /dev/null; then
    echo "doctl is not installed. Please install it first."
    exit 1
fi

if ! doctl account get &> /dev/null; then
    echo "Not authenticated with DigitalOcean. Please run 'doctl auth init' first."
    exit 1
fi

# Verify and build
npm install
npm run build

# Deploy to DigitalOcean
APP_NAME="allervie-analytics-dashboard"
APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo "Creating new app..."
    doctl apps create --spec .do/app.yaml
    
    APP_ID=$(doctl apps list --format "ID,Spec.Name" --no-header | grep "$APP_NAME" | awk '{print $1}')
else
    echo "Updating existing app with ID: $APP_ID"
    doctl apps update $APP_ID --spec .do/app.yaml
fi

echo "Deployment initiated!"
echo "App ID: $APP_ID"
echo "To monitor deployment: node scripts/monitoring-script.js $APP_ID"
```

### 2. Monitoring Script (monitoring-script.js)

This Node.js script helps monitor deployment status and diagnose issues. See the full script in the repository at `/scripts/monitoring-script.js`.

```bash
# Run with:
node scripts/monitoring-script.js [APP_ID]
```

## Deployment Steps

1. **Prepare your code**:
   - Ensure all code changes are committed and pushed to GitHub
   - Verify environment variables in `.do/app.yaml`
   - Update Google OAuth credentials if needed

2. **Execute the deployment script**:
   ```bash
   ./deploy-digitalocean.sh
   ```

3. **Monitor the deployment**:
   ```bash
   node scripts/monitoring-script.js APP_ID
   ```

4. **Verify the deployment**:
   - Check that the app is accessible at the provided URL
   - Verify the health check endpoint (`/api/health`)
   - Test the Google OAuth flow
   - Check that data is being displayed correctly

## Troubleshooting

### Common Issues

1. **Deployment Fails with Package Manager Errors**:
   - Issue: DigitalOcean's buildpack conflicts with manual package manager installation
   - Solution: Remove any `npm install -g pnpm` commands from build scripts

2. **Environment Variables Not Available**:
   - Issue: Environment variables not properly configured in app.yaml
   - Solution: Verify all required environment variables are set with correct scope

3. **Health Check Failures**:
   - Issue: Application health check endpoint failing
   - Solution: Verify the health check endpoint is implemented correctly and responding

4. **Authentication Failures**:
   - Issue: OAuth flow not working in production
   - Solution: Ensure OAuth redirect URIs match the production URL

5. **API Connection Issues**:
   - Issue: Frontend cannot connect to API endpoints
   - Solution: Verify API URL configuration and CORS settings, check that rewrites in next.config.ts are correctly set up

### Monitoring Commands

```bash
# View app status
doctl apps get APP_ID

# View deployment status
doctl apps get-deployment APP_ID DEPLOYMENT_ID

# View logs
doctl apps logs APP_ID

# Follow logs in real-time
doctl apps logs APP_ID --follow

# View component logs
doctl apps logs APP_ID --component web
```

## Post-Deployment Verification

After deployment, verify that:

1. **Application is accessible** at the provided DigitalOcean URL
2. **Health check endpoint** is responding correctly (`/api/health`)
3. **Authentication flow** works correctly with Google OAuth
4. **API data** is being fetched and displayed correctly
5. **Error handling** is working as expected

## Continuous Deployment

To enable continuous deployment:

1. Ensure `deploy_on_push: true` is set in your app.yaml
2. Push changes to the branch specified in your GitHub configuration
3. DigitalOcean will automatically deploy new changes

## Conclusion

This deployment guide provides a comprehensive approach to deploying the Allervie Dashboard to DigitalOcean App Platform. By following these steps and using the provided scripts, you can ensure a smooth deployment process and establish a foundation for ongoing maintenance and monitoring.
