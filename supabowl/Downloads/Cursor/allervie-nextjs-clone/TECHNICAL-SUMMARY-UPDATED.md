# Allervie Analytics Dashboard - Technical Summary

## Project Overview

The Allervie Analytics Dashboard is a Next.js-based web application designed to provide marketing analytics and visualization of Google Ads performance data. This project represents a complete rebuild of a previous dashboard implementation, transitioning from a React + FastAPI/Flask architecture to a more integrated Next.js solution with API routes serving as the backend.

## Project Architecture

### Current Architecture

The application follows a modern Next.js architecture with the App Router pattern:

```
┌──────────────────────────────────────┐     ┌────────────────┐
│              Next.js                 │     │                │
│  ┌─────────────┐  ┌────────────────┐ │     │                │
│  │  Frontend   │  │ API Routes     │ │━━━━▶│   Google Ads   │
│  │ Components  │◀━▶│ (Backend)     │ │◀━━━━│      API       │
│  └─────────────┘  └────────────────┘ │     │                │
└──────────────────────────────────────┘     └────────────────┘
```

### Key Components

1. **Frontend Components**:
   - MetricCard: Reusable component for displaying performance metrics
   - GoogleAdsPerformance: Dashboard for Google Ads performance metrics
   - GoogleAdsCampaigns: Table for campaign-level data

2. **API Routes**:
   - /api/google-ads/performance: Performance data endpoint
   - /api/google-ads/campaigns: Campaign data endpoint
   - /api/auth/*: Authentication endpoints
   - /api/health: Health check endpoint

3. **External Integrations**:
   - Google Ads API: Source of advertising performance data

## Technology Stack

- **Framework**: Next.js 14.0.4
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks (useState, useEffect)
- **Authentication**: OAuth 2.0 with Google
- **Data Visualization**: Chart.js
- **Deployment**: DigitalOcean App Platform

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

## Current Deployment Challenges

The primary challenge is a package manager conflict in the deployment process:

1. **Package Manager Conflict**:
   - The GitHub repository contains a `pnpm-lock.yaml` file
   - DigitalOcean's buildpack detects this file and uses pnpm for dependency installation
   - The build command in `.do/app.yaml` is set to `npm ci && npm run build`
   - This causes a failure because `npm ci` requires `package-lock.json`

2. **Deployment Configuration Issue**:
   - The Dockerfile and app.yaml may have inconsistent configurations
   - Node.js version in Dockerfile may not match the version in package.json
   - Port configuration may be inconsistent between Dockerfile and app.yaml

## Implemented Solutions

A fix-deployment.sh script has been created to address these issues:

1. **Package Manager Consistency**:
   - Removes `pnpm-lock.yaml` if it exists
   - Ensures `package-lock.json` is used for npm-based builds
   - Updates package.json to remove any packageManager field

2. **Configuration Updates**:
   - Updates next.config.js with `output: 'standalone'` for DigitalOcean deployment
   - Updates the Dockerfile to use Node.js 22-alpine
   - Sets consistent port (8080) across Dockerfile and app.yaml

3. **Environment Variables**:
   - Configures all necessary environment variables in app.yaml
   - Sets up proper secrets handling for sensitive credentials

## Data Flow

The application follows this data flow pattern:

1. User authenticates via Google OAuth
2. Frontend components request data from Next.js API routes
3. API routes authenticate with and request data from Google Ads API
4. Data is processed and returned to frontend
5. Frontend components render visualizations of the data

## Security Considerations

1. **Authentication**: OAuth 2.0 flow with secure token storage
2. **Environment Variables**: Sensitive information stored as secrets
3. **HTTP Headers**: Security headers configured in next.config.js
4. **CSRF Protection**: State parameters in OAuth flow
5. **API Security**: Proper authentication for all API calls

## Performance Optimizations

1. **Server-Side Rendering**: Improved initial load performance
2. **Standalone Output**: Optimized build for containerized deployment
3. **Error Handling**: Graceful degradation with fallbacks to mock data
4. **Caching**: API responses cached where appropriate

## Future Enhancements

1. **Google Analytics 4 Integration**: Adding GA4 alongside Google Ads
2. **Advanced Campaign Management**: Budget optimization tools
3. **Custom Date Range Selection**: Enhanced time period analysis
4. **Enhanced Visualizations**: More interactive charts and graphs
5. **User Management**: Role-based access control

## Conclusion

The Allervie Analytics Dashboard is a comprehensive marketing analytics solution built with modern web technologies. The current deployment issues are being addressed with the fix-deployment.sh script, which ensures consistent package manager usage and proper configuration for DigitalOcean App Platform deployment.

Once successfully deployed, the dashboard will provide marketing teams with valuable insights into their Google Ads performance, enabling data-driven decision making and campaign optimization.
