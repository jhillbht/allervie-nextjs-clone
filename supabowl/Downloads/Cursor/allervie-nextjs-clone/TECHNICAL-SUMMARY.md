# Allervie Analytics Dashboard - Technical Project Summary

## Project Overview

The Allervie Analytics Dashboard is a Next.js-based web application designed to visualize and analyze marketing performance data from Google Ads. The project represents a full rebuild of a previous dashboard, transitioning from a React + Flask architecture to a more integrated Next.js solution with API routes.

## Architecture

### Current Architecture

```
┌──────────────────────────────────┐     ┌────────────────┐
│              Next.js             │     │                │
│  ┌─────────────┐  ┌────────────┐ │     │                │
│  │  Frontend   │  │ API Routes │ │━━━━▶│   Google Ads   │
│  │ Components  │◀━▶│ (Backend) │ │◀━━━━│      API       │
│  └─────────────┘  └────────────┘ │     │                │
└──────────────────────────────────┘     └────────────────┘
```

### Previous Architecture (Being Replaced)

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│    React.js    │━━━━▶│    Flask API   │━━━━▶│   Google Ads   │
│    Frontend    │◀━━━━│    Backend     │◀━━━━│      API       │
│                │     │                │     │                │
└────────────────┘     └────────────────┘     └────────────────┘
```

## Technology Stack

- **Frontend Framework**: Next.js 14.0.4
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks (useState, useEffect)
- **Data Visualization**: Chart.js with react-chartjs-2
- **Authentication**: OAuth 2.0 with Google
- **API Integration**: Google Ads API
- **Deployment**: DigitalOcean App Platform

## Core Components

### Frontend Components

1. **MetricCard**: Reusable component for displaying performance metrics with change indicators
2. **GoogleAdsPerformance**: Container for displaying multiple metrics in a dashboard layout
3. **GoogleAdsCampaigns**: Table component for displaying campaign-level data
4. **UI Components**: Button, Card, and other reusable UI elements

### API Routes

1. **/api/google-ads/performance**: Fetches aggregate performance metrics
2. **/api/google-ads/campaigns**: Fetches campaign-level data
3. **/api/google-ads/ad_groups**: Fetches ad group-level data
4. **/api/google-ads/search_terms**: Fetches search term performance data
5. **/api/health**: Health check endpoint for monitoring service status
6. **/api/dashboard/summary**: Provides summary metrics for the dashboard

## Data Flow

1. User authenticates via Google OAuth
2. Frontend components request data from Next.js API routes
3. API routes make authenticated requests to Google Ads API
4. Data is formatted and returned to frontend components
5. Components render visualizations and tables with the data
6. If API requests fail, the system falls back to mock data

## Deployment Architecture

The application is deployed on DigitalOcean App Platform with the following configuration:

```
┌───────────────────────────────────────────────┐
│             DigitalOcean App Platform         │
│                                               │
│  ┌─────────────────┐                          │
│  │                 │                          │
│  │   Next.js App   │━━━━▶     External APIs   │
│  │                 │                          │
│  └─────────────────┘                          │
│           ▲                                   │
│           │                                   │
└───────────┼───────────────────────────────────┘
            │                      
    ┌───────────────┐     
    │  GitHub Repo  │      
    │               │     
    └───────────────┘      
```

## Current Deployment Issues

The deployment to DigitalOcean App Platform is experiencing the following issues:

1. **Package Manager Conflict**: The deployment process is detecting a `pnpm-lock.yaml` file while the project is configured to use npm, leading to build failures.

2. **Build Command Mismatch**: The system is attempting to run `remix vite:build` instead of `next build`, indicating a potential configuration issue with the build process.

3. **Port Configuration Inconsistency**: The Dockerfile is configured to use port 8080, but the DigitalOcean app.yaml is set to use port 3000.

4. **Node.js Version Mismatch**: The package.json requires Node.js 22.x, but the Dockerfile is using Node.js 18-alpine.

## Implemented Fixes

A comprehensive fix script has been created to address these issues:

1. **Package Manager Fix**: Remove any `pnpm-lock.yaml` file and ensure `package-lock.json` is present.

2. **Build Configuration Fix**: Update the build command in app.yaml to `npm ci && npm run build` to ensure proper dependency installation before building.

3. **Port Configuration Fix**: Update app.yaml to use http_port 8080 to match the Dockerfile configuration.

4. **Node.js Version Fix**: Update the Dockerfile to use `node:22-alpine` to match the requirements in package.json.

5. **Next.js Configuration Fix**: Ensure `next.config.js` has the `output: 'standalone'` setting for proper deployment on DigitalOcean.

## Security Considerations

1. **OAuth Implementation**: The application uses OAuth 2.0 for secure authentication with Google.

2. **Token Storage**: Authentication tokens are stored in HTTP-only cookies for security.

3. **Environment Variables**: Sensitive information is stored in environment variables, not in the codebase.

4. **CSRF Protection**: State parameters are used in the OAuth flow to prevent CSRF attacks.

5. **HTTP Headers**: Security headers are set in next.config.js to prevent common web vulnerabilities.

## Performance Optimizations

1. **Server-Side Rendering**: Utilized for improved loading performance and SEO.

2. **Automatic Fallbacks**: System falls back to mock data when API requests fail.

3. **Error Boundaries**: Implemented to prevent the entire application from crashing due to component errors.

4. **Caching**: API responses are cached where appropriate to reduce redundant requests.

## Future Enhancements

1. **Google Analytics 4 Integration**: Adding support for GA4 data alongside Google Ads.

2. **Advanced Campaign Management**: Adding budget optimization tools and recommendations.

3. **Custom Date Range Selection**: Allowing users to select specific date ranges for analysis.

4. **Enhanced Visualizations**: Adding more interactive and customizable charts and graphs.

5. **User Authentication**: Implementing direct user login with role-based access controls.

## Monitoring and Maintenance

1. **Health Check Endpoint**: Available at `/api/health` for monitoring service status.

2. **Logging Strategy**: Comprehensive logging throughout the application for debugging.

3. **Deployment Monitoring**: Custom scripts for monitoring DigitalOcean deployments.

4. **Error Tracking**: Detailed error tracking for both frontend and backend components.

## Conclusion

The Allervie Analytics Dashboard represents a significant improvement over the previous implementation, with a more integrated architecture, improved performance, and better maintainability. The current deployment issues are being addressed with the implemented fixes, and the project is well-positioned for future enhancements.
