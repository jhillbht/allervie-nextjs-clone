# Allervie Dashboard Deployment Update

## What's New

We've created comprehensive deployment tools for the Allervie Dashboard to simplify the process of deploying to DigitalOcean App Platform:

1. **Deployment Script**: `deploy-digitalocean.sh`
   - Automated deployment to DigitalOcean App Platform
   - Handles authentication verification
   - Checks for existing apps or creates a new one
   - Monitors deployment progress
   - Provides helpful status updates and commands

2. **Monitoring Script**: `scripts/monitoring-script.js`
   - Provides detailed information about deployment status
   - Analyzes and diagnoses common deployment issues
   - Checks health endpoint functionality
   - Provides component-specific analysis
   - Shows helpful monitoring commands

3. **Deployment Guide**: `DEPLOYMENT-GUIDE.md`
   - Comprehensive guide for deploying to DigitalOcean
   - Configuration file explanations
   - Troubleshooting common issues
   - Step-by-step deployment instructions
   - Post-deployment verification steps

## How to Use

### Deploying

1. Make sure you have `doctl` installed and authenticated:
   ```bash
   # Install doctl (macOS)
   brew install doctl
   
   # Authenticate
   doctl auth init
   ```

2. Run the deployment script:
   ```bash
   ./deploy-digitalocean.sh
   ```

### Monitoring

After deployment starts, monitor the progress with:

```bash
node scripts/monitoring-script.js [APP_ID]
```

Replace `[APP_ID]` with your app ID, or omit it to use the most recent app.

## Configuration

The deployment uses the following files:

- `.do/app.yaml`: DigitalOcean App Platform configuration
- `next.config.ts`: Next.js configuration with optimizations for production
- `Dockerfile`: Container configuration optimized for DigitalOcean
- `.env.production`: Production environment variables

## Troubleshooting

If you encounter issues, refer to the monitoring script output for specific diagnostics or check the `DEPLOYMENT-GUIDE.md` for common issues and solutions.

You can also check the logs directly:

```bash
# View all logs
doctl apps logs APP_ID

# Follow logs in real-time
doctl apps logs APP_ID --follow

# View logs for a specific component
doctl apps logs APP_ID --component web
```

## Next Steps

After successful deployment:

1. Verify the application is accessible at the provided URL
2. Check the health endpoint (`/api/health`)
3. Test the Google OAuth flow
4. Ensure data is being displayed correctly
