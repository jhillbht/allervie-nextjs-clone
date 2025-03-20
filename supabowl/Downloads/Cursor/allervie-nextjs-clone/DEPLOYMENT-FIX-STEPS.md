# Allervie Dashboard Deployment Fix Steps

This document outlines the specific steps to fix the deployment issues with the Allervie Analytics Dashboard on DigitalOcean App Platform.

## Current Deployment Status

The deployment is currently failing during the build process with the following error:

```
npm error code EUSAGE
npm error
npm error The `npm ci` command can only install with an existing package-lock.json or
npm error npm-shrinkwrap.json with lockfileVersion >= 1. Run an install with npm@5 or
npm error later to generate a package-lock.json file, then try again.
```

## Root Cause Analysis

The build failure is due to a package manager conflict:

1. The build system detects a `pnpm-lock.yaml` file in the GitHub repository and uses pnpm for dependency installation.
2. The build command in `.do/app.yaml` is set to `npm ci && npm run build`, which requires a `package-lock.json` file.
3. Since pnpm is being used instead of npm, the `package-lock.json` file is not being utilized, causing the `npm ci` command to fail.

## Step-by-Step Fix

1. **Execute the fix-deployment.sh script**

   The repository already contains a `fix-deployment.sh` script that addresses these issues. Run it locally:

   ```bash
   cd /Users/supabowl/Downloads/Cursor/allervie-nextjs-clone
   chmod +x fix-deployment.sh  # Ensure the script is executable
   ./fix-deployment.sh
   ```

   This script:
   - Removes any `pnpm-lock.yaml` file if it exists
   - Updates package.json to remove any packageManager field
   - Updates next.config.js with the correct configuration
   - Updates the Dockerfile to use Node.js 22
   - Updates .do/app.yaml with the correct configuration

2. **Push changes to GitHub**

   After running the fix script, commit and push the changes to ensure the updated configuration is used for deployment:

   ```bash
   git add .
   git commit -m "Fix: Update package manager configuration for DigitalOcean deployment"
   git push origin main
   ```

3. **Redeploy the application**

   Run the deployment script to deploy the application with the fixed configuration:

   ```bash
   ./deploy-digitalocean.sh
   ```

4. **Monitor the deployment**

   The `deploy-digitalocean.sh` script includes monitoring of the deployment process. You can also use:

   ```bash
   # Get the APP_ID from the deployment script output
   doctl apps logs APP_ID --follow
   ```

## Alternative Solutions

If the fix-deployment.sh script doesn't solve the issue, there are two alternative approaches:

### Option 1: Update the build command

Change the build command in `.do/app.yaml` to use pnpm instead of npm:

```yaml
build_command: pnpm install && pnpm build
```

### Option 2: Switch to Docker deployment

Use the Dockerfile included in the repository for direct container deployment:

```yaml
services:
  - name: nextjs-dashboard
    dockerfile_path: Dockerfile
    github:
      repo: jhillbht/allervie-nextjs-clone
      branch: main
    # Other configuration...
```

## Verification Steps

After deployment, verify that:

1. The application is running by accessing the URL provided by DigitalOcean
2. The health check endpoint at `/api/health` returns a 200 OK status
3. The dashboard loads with all components visible
4. API calls to Google Ads API are working correctly

If any issues persist, check the logs for specific error messages:

```bash
doctl apps logs APP_ID
```

## Conclusion

The deployment issue is a common packaging conflict that occurs when mixing package managers. The provided fix ensures that the build process uses a consistent package manager throughout, allowing the application to build and deploy successfully.
