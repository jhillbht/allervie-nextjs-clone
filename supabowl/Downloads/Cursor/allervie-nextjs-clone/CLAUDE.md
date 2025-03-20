# Allervie Dashboard Next.js Implementation Guide

## Deployment Status and Troubleshooting Notes

The current deployment is experiencing issues with the DigitalOcean App Platform. The key problems identified:

1. **Package Manager Conflict**: The deployment is detecting `pnpm-lock.yaml` but the project is set up to use npm, causing build failures
2. **Build Command Mismatch**: The build command `npm ci && npm run build` fails because pnpm is being used instead of npm
3. **Port Configuration Inconsistency**: Dockerfile is set for port 8080 but DigitalOcean app.yaml uses port 3000
4. **Node.js Version Mismatch**: Package.json requires Node.js 22.x but Dockerfile uses 18.x

A fix script has been created at `/Users/supabowl/Downloads/Cursor/allervie-nextjs-clone/fix-deployment.sh` to address these issues.

## Detailed Deployment Error

The current deployment fails with this specific error:

```
project contains pnpm-lock.yaml, using pnpm
...
npm error code EUSAGE
npm error
npm error The `npm ci` command can only install with an existing package-lock.json or
npm error npm-shrinkwrap.json with lockfileVersion >= 1.
```

This indicates a package manager conflict where the build system detects pnpm-lock.yaml and uses pnpm for dependency installation, but then attempts to run `npm ci` which requires package-lock.json.

## Quick Start Guide (From Blank Terminal)

### 1. Clone and Setup
```bash
# Clone repository (if needed)
git clone https://github.com/yourusername/allervie-nextjs-clone.git
cd allervie-nextjs-clone

# Install dependencies
npm install
```

### 2. Environment Configuration
1. Create a `.env.local` file in the root directory with these settings:
   ```
   # Backend API URL for development
   NEXT_PUBLIC_API_URL=http://localhost:5002
   
   # Google OAuth Configuration (for production)
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   OAUTH_REDIRECT_URI=http://localhost:3000/api/auth/callback
   ```

### 3. Start Backend API
```bash
# Navigate to Flask backend directory
cd /path/to/Allervie\ Front-Back\ APIs
cd backend

# Start Flask backend
python app.py
```

### 4. Start Next.js Dashboard
```bash
# Open a new terminal and navigate to the Next.js project
cd /path/to/allervie-nextjs-clone

# Start development server
npm run dev

# Open browser and navigate to:
# http://localhost:3000
```

### 5. Authentication Flow
1. The dashboard will try to fetch data from the Flask backend
2. OAuth flow is handled through the backend API
3. Data will be displayed in the dashboard once authenticated

## DigitalOcean Deployment Process

1. **Fix Identified Issues**:
   ```bash
   cd /Users/supabowl/Downloads/Cursor/allervie-nextjs-clone
   chmod +x fix-deployment.sh  # Ensure the script is executable
   ./fix-deployment.sh
   ```

2. **Push changes to GitHub**:
   ```bash
   git add .
   git commit -m "Fix: Update package manager configuration for DigitalOcean deployment"
   git push origin main
   ```

3. **Deploy to DigitalOcean**:
   ```bash
   ./deploy-digitalocean.sh
   ```

4. **Monitor Deployment**:
   ```bash
   # Get the APP_ID from the deployment script output
   doctl apps logs APP_ID --follow
   ```

5. **Test Deployed Application**:
   ```bash
   # Use the App URL from the deployment output
   curl https://YOUR_APP_URL/api/health
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

## Features Implemented

- **Next.js App Router Architecture**: Modern, efficient routing system
- **Server-Side API Routes**: Secure proxy to Flask backend
- **Google Ads API Integration**: Complete integration with performance metrics
- **TypeScript Type Safety**: Fully typed components and API responses
- **Responsive Dashboard UI**: Works on all screen sizes 
- **Interactive Data Visualization**: Charts, metrics cards, and campaign tables
- **Error Handling & Fallbacks**: Graceful degradation with mock data
- **Robust Console Logging**: Comprehensive debugging information

## Key Components

- **MetricCard**: Reusable component for displaying metrics with change indicators
- **GoogleAdsPerformance**: Displays key Google Ads performance metrics
- **GoogleAdsCampaigns**: Table view of campaign performance data
- **API Routes**: Server-side endpoints that proxy requests to Flask backend

## Key Commands

- Start development server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm start`
- Lint code: `npm run lint`
- Dashboard access point: http://localhost:3000/dashboard
- API endpoints: http://localhost:3000/api/google-ads/*

## Code Style Guidelines

- **TypeScript**: Use strict type checking with proper interfaces
- **React Components**: Function components with React hooks
- **Error Handling**: Try/catch blocks with fallbacks to mock data
- **API Clients**: Axios instances with typed responses
- **Naming**: PascalCase for components, camelCase for functions and variables
- **Security**: No credentials in code; use environment variables

## Project Structure

```
/src
  /app                 # Next.js App Router pages and API routes
    /api               # API routes for proxying requests to Flask backend
      /google-ads      # Google Ads API routes
    /dashboard         # Dashboard page
    page.tsx           # Homepage (redirects to dashboard)
  /components          # Reusable React components
    /dashboard         # Dashboard-specific components
    /ui                # Generic UI components
  /lib                 # Utility functions and shared code
    google-ads-client.ts   # Client for Google Ads API
    mock-data.ts           # Mock data for development and fallback
```

## Troubleshooting

- **Backend Connection Issues**: Verify NEXT_PUBLIC_API_URL is set correctly
- **API Errors**: Check browser console for detailed error logs
- **Authentication Problems**: Verify OAuth is properly configured in backend
- **Component Errors**: Check React component props and types
- **Missing Data**: Inspect network requests in browser developer tools
- **Environment Variables**: Make sure `.env.local` is present and correctly formatted

## DigitalOcean Deployment Configuration

1. Updated `.do/app.yaml` in the root directory:
   ```yaml
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
   ```

### doctl Command Reference

Key doctl commands for managing the deployment:

```bash
# List all apps
doctl apps list

# Get app details
doctl apps get APP_ID

# View logs
doctl apps logs APP_ID

# View deployment status
doctl apps get-deployment APP_ID DEPLOYMENT_ID
```

### Environment Variables for Production

| Variable | Description | Environment |
|----------|-------------|-------------|
| `NEXT_PUBLIC_API_URL` | URL of the Flask backend API | Build and Runtime |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Runtime (Secret) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Runtime (Secret) |
| `OAUTH_REDIRECT_URI` | OAuth redirect URI | Runtime |
| `NODE_ENV` | Node.js environment (production/development) | Runtime |

## Future Enhancements

- **Google Analytics 4 Integration**: To be added in next phase
- **Advanced Campaign Management**: Budget optimization and analysis
- **Custom Date Range Selection**: User-configurable time periods
- **Enhanced Data Visualization**: Interactive and customizable charts
- **User Authentication**: Direct user login with role-based access
- **Data Export**: CSV/Excel export capabilities
