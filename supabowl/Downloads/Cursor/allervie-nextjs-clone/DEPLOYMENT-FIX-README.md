# Allervie Dashboard Deployment Fix

This document outlines the fixes applied to resolve deployment issues with the Allervie Dashboard on DigitalOcean App Platform.

## Issue Identified

The deployment was failing with the following error:

```
Error: Cannot find matching keyid: {"signatures":[{"sig":"MEUCIQDX5rBiPPLMcFTegu9hjp64z2gJTYuIrMwCAG/7HZMR3QIgHEf7HDdZ8avqrnaKqBA7Q8KezVQX0nEd0cwJCla+rWA=","keyid":"SHA256:DhQ8wR5APBvFHLF/+Tc+AYvPOdTpcIDqOhxsBHRwC7U"}],"keys":[{"expires":null,"keyid":"SHA256:jl3bwswu80PjjokCgh0o2w5c2U4LhQAE57gj9cz1kzA","keytype":"ecdsa-sha2-nistp256","scheme":"ecdsa-sha2-nistp256","key":"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1Olb3zMAFFxXKHiIkQO5cJ3Yhl5i6UPp+IhuteBJbuHcA5UogKo0EWtlWwW6KSaKoTNEYL7JlCQiVnkhBktUgg=="}]}
```

This error occurred during the `corepack enable pnpm && pnpm install` command in the Dockerfile, which was being used to install dependencies.

## Changes Made

### 1. Updated Dockerfile

- Changed the base Node.js image from Node.js 22 to Node.js 20.18.0 to ensure compatibility with DigitalOcean App Platform
- Modified the dependency installation process to use `npm ci` instead of `pnpm install`
- Updated the health check command to use `wget` instead of `curl` (which might not be available in the Alpine image)
- Made sure the permissions were properly set for the Next.js directory

### 2. Updated package.json

- Updated the Node.js engine version from `22.x` to `20.x` to match the Dockerfile

### 3. Created next.config.js

- Added a JavaScript version of the Next.js configuration (next.config.js) alongside the TypeScript version (next.config.ts)
- This ensures build systems that might not process TypeScript files correctly will have a JS fallback

### 4. Updated app.yaml

- Modified the run command from `node .next/standalone/server.js` to `node server.js`
- Ensured all environment variables are properly defined

## How to Use the Fix

1. Clone the repository with the fix branch:
   ```bash
   git clone -b fix-deploy-issue https://github.com/jhillbht/allervie-nextjs-clone.git
   cd allervie-nextjs-clone
   ```

2. Run the deployment fix script:
   ```bash
   ./deploy-fixes.sh
   ```

3. Monitor the deployment:
   ```bash
   doctl apps logs allervie-analytics-dashboard --follow
   ```

## Additional Notes

- The deployment script (`deploy-fixes.sh`) will automatically:
  - Check if the app exists on DigitalOcean
  - Create or update the app with the new configuration
  - Monitor the deployment progress
  - Display the deployment status and logs

- If you encounter any issues with the deployment, you can check the logs using:
  ```bash
  doctl apps logs YOUR_APP_ID
  ```

- To get your app ID, run:
  ```bash
  doctl apps list
  ```

## Verification

After deploying, verify that:

1. The app is deployed successfully
2. The health check endpoint (`/api/health`) returns a 200 OK status
3. The dashboard is accessible and displaying data correctly

## References

- [DigitalOcean App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [Node.js on Alpine Docker Images](https://hub.docker.com/_/node/)