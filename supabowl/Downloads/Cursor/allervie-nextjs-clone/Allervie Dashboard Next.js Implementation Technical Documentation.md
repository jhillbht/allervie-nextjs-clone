# Allervie Dashboard Next.js Implementation Technical Documentation

## Executive Summary

This document outlines the comprehensive implementation of the Allervie Dashboard in Next.js, which focuses on integrating Google Ads API data with plans to incorporate Google Analytics 4 (GA4) in the future. The project represents a complete rebuild of the original React-based dashboard, leveraging Next.js's server-side rendering capabilities, improved routing, and modern React patterns to create a more performant and maintainable application.

## Project Overview

The Allervie Dashboard provides marketing performance analytics for Allervie Health's digital marketing campaigns. The primary focus is on Google Ads metrics, with real-time data visualization and campaign management capabilities. The dashboard is designed to help marketing teams track campaign performance, optimize ad spend, and identify growth opportunities.

### Key Features

- Real-time Google Ads performance metrics visualization
- Campaign performance tracking and analysis
- Google OAuth authentication
- Robust error handling and logging
- Responsive design for all device sizes
- Fallback to mock data when API connections fail

## Architecture

### System Architecture

The application follows a modern web architecture with clear separation of concerns:

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│    Next.js     │━━━━▶│    FastAPI     │━━━━▶│   Google Ads   │
│    Frontend    │◀━━━━│    Backend     │◀━━━━│      API       │
│                │     │                │     │                │
└────────────────┘     └────────────────┘     └────────────────┘
```

1. **Frontend (Next.js)**: 
   - Handles UI rendering and client-side state management
   - Implements server-side API routes that proxy requests to the backend
   - Provides authentication flow and token management

2. **Backend (FastAPI)**:
   - Manages Google Ads API authentication and token refresh
   - Handles complex data aggregation and processing
   - Provides standardized API endpoints for the frontend

3. **Google Ads API**:
   - Source of all advertising performance data
   - Requires OAuth 2.0 authentication

### Project Structure

```
/src
  /app                 # Next.js App Router pages and API routes
    /api               # API routes for proxying requests to FastAPI backend
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

## Frontend Implementation

### Component Hierarchy

```
Dashboard Page
├── GoogleAdsPerformance
│   └── MetricCard (multiple instances)
├── GoogleAdsCampaigns
│   └── Campaign Table Rows
└── Future GA4 Components
```

### Key Components

#### MetricCard

A reusable component that displays a single performance metric with its value and percentage change. Features include:

- Appropriate formatting for different data types (numbers, percentages, currency)
- Color-coded indicators for positive/negative changes
- Support for inverse coloring (e.g., for metrics where lower is better)
- Animated hover effects for better user experience

#### GoogleAdsPerformance

A container component that displays a collection of metrics related to Google Ads performance:

- Fetches real-time data from the Google Ads API
- Supports manual and automatic refresh with configurable intervals
- Displays loading states and error messages
- Falls back to mock data when API requests fail

#### GoogleAdsCampaigns

A table component that displays detailed campaign performance data:

- Sortable columns for easy comparison
- Status indicators for active/paused campaigns
- Formatted metrics with appropriate units (currency, percentages)
- Pagination for handling large datasets

### API Integration & Data Flow

The application uses a structured approach to data fetching:

1. **Client Utilities**: The `google-ads-client.ts` module provides typed functions for fetching data from the API.

2. **API Routes**: Next.js API routes proxy requests to the FastAPI backend, handling errors and providing fallbacks.

3. **React Components**: Components use React hooks (`useState`, `useEffect`) to manage state and trigger data fetching.

4. **Error Handling**: Comprehensive error handling at each layer ensures a smooth user experience even when errors occur.

### Detailed Logging Strategy

Robust console logging is implemented throughout the application to aid in debugging and monitoring:

```typescript
// Example from google-ads-client.ts
export async function getAdsPerformance(...) {
  // Log the start of the request with parameters
  console.log('Fetching Google Ads performance data', { 
    startDate, endDate, previousPeriod, useMockData 
  });
  
  try {
    const response = await api.get('/api/google-ads/performance', { params });
    
    // Log successful response with data summary
    console.log('Successfully fetched Google Ads performance data', {
      metrics: Object.keys(response.data),
      timestamp: new Date().toISOString()
    });
    
    return response.data;
  } catch (error) {
    // Log detailed error information
    console.error('Error fetching Google Ads performance data:', error);
    console.error('Request details:', { startDate, endDate, previousPeriod });
    
    if (axios.isAxiosError(error)) {
      console.error('API response:', error.response?.data);
      console.error('Status code:', error.response?.status);
    }
    
    // Log fallback action
    console.log('Falling back to mock Google Ads performance data');
    return mockAdsPerformance;
  }
}
```

API routes implement similar logging to track requests through the system:

```typescript
// Example from performance API route
export async function GET(request: NextRequest): Promise<NextResponse> {
  // Log incoming request
  console.log(`Google Ads performance request received`, {
    params: Object.fromEntries(request.nextUrl.searchParams.entries()),
    headers: {
      // Log only non-sensitive headers
      'content-type': request.headers.get('content-type'),
      'user-agent': request.headers.get('user-agent'),
    },
    timestamp: new Date().toISOString()
  });
  
  // ... implementation ...
  
  // Log response
  console.log(`Google Ads performance response sent`, {
    status: 200,
    dataSize: JSON.stringify(response.data).length,
    timestamp: new Date().toISOString()
  });
}
```

## Google OAuth Implementation

The OAuth flow is implemented with security and user experience in mind:

### Authentication Flow

1. **Initiation**: User clicks "Connect to Google Ads" button
2. **Redirect**: User is redirected to Google's OAuth consent screen
3. **Authorization**: User grants permission to access their Google Ads data
4. **Callback**: Google redirects back to the application with an authorization code
5. **Token Exchange**: Application exchanges code for access and refresh tokens
6. **Storage**: Tokens are securely stored for future use
7. **API Access**: Access token is used for API requests and refreshed when needed

### OAuth Configuration

The OAuth configuration includes:

```typescript
// OAuth Configuration
const OAUTH_CONFIG = {
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  redirectUri: process.env.OAUTH_REDIRECT_URI || 'http://localhost:3000/api/auth/callback',
  scopes: [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
  ]
};
```

### Token Management

The application implements a smart token management system that:

1. Stores refresh tokens securely
2. Automatically refreshes access tokens when they expire
3. Handles token rotation and revocation
4. Provides fallback mechanisms when token operations fail

### Security Considerations

- CSRF protection using state parameters
- Secure storage of tokens in HTTP-only cookies or encrypted session storage
- Validation of token responses
- Protection against common OAuth vulnerabilities

## Backend API Integration

The Next.js application integrates with the FastAPI backend through a set of API routes:

### API Route Implementation

Each API route in the Next.js application:

1. Receives requests from the frontend
2. Forwards them to the corresponding FastAPI backend endpoint
3. Processes the response
4. Handles errors and provides fallbacks
5. Returns data in a consistent format

Example API route:

```typescript
// /api/google-ads/performance/route.ts
export async function GET(request: NextRequest): Promise<NextResponse> {
  const searchParams = request.nextUrl.searchParams;
  
  // Extract query parameters
  const startDate = searchParams.get('start_date');
  const endDate = searchParams.get('end_date');
  const previousPeriod = searchParams.get('previous_period') === 'true';
  
  // Build request to FastAPI backend
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (previousPeriod) params.previous_period = 'true';
  
  try {
    // Make request to FastAPI backend
    const response = await axios.get(`${BACKEND_API_URL}/api/google-ads/performance`, { 
      params,
      headers: {
        Authorization: request.headers.get('Authorization') || '',
      },
    });
    
    // Return response to frontend
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error fetching Google Ads performance data:', error);
    
    // Fall back to mock data
    return NextResponse.json(mockAdsPerformance);
  }
}
```

### Error Handling Strategy

The application implements a layered error handling strategy:

1. **API Client Layer**: Catches network errors, timeouts, and API errors
2. **API Route Layer**: Handles backend errors and provides fallbacks
3. **Component Layer**: Displays appropriate error messages to the user

### Fallback Mechanisms

When API requests fail, the application gracefully degrades:

1. First attempts to use cached data if available
2. Falls back to mock data if no cache is available
3. Displays user-friendly error messages
4. Provides retry options for temporary failures

## Testing Approach

The application includes comprehensive testing at multiple levels:

### API Connection Testing

The application implements robust API connection testing:

```typescript
// Example connection test function
async function testApiConnection() {
  console.log('Testing API connection to backend...');
  
  try {
    const response = await axios.get(`${BACKEND_API_URL}/api/health`);
    
    console.log('Backend API connection test results:', {
      status: response.status,
      data: response.data,
      latency: performance.now() - startTime
    });
    
    return true;
  } catch (error) {
    console.error('Backend API connection test failed:', error);
    
    // Log detailed error information
    if (axios.isAxiosError(error)) {
      console.error('Status:', error.response?.status);
      console.error('Data:', error.response?.data);
      console.error('Network error:', error.isAxiosError && !error.response);
    }
    
    return false;
  }
}
```

### End-to-End Testing

The application includes end-to-end tests that verify:

1. Authentication flow
2. Data fetching and display
3. User interactions
4. Error handling

### Component Testing

Individual components are tested to ensure they:

1. Render correctly with different props
2. Handle loading and error states appropriately
3. Correctly format and display data
4. Respond properly to user interactions

## Deployment to DigitalOcean App Platform

### Deployment Architecture

The deployment architecture leverages DigitalOcean App Platform's capabilities:

```
┌───────────────────────────────────────────────┐
│             DigitalOcean App Platform         │
│                                               │
│  ┌─────────────────┐     ┌─────────────────┐  │
│  │                 │     │                 │  │
│  │   Next.js App   │━━━━▶│   FastAPI      │  │
│  │   (Web Service) │◀━━━━│   (API Service) │  │
│  │                 │     │                 │  │
│  └─────────────────┘     └─────────────────┘  │
│           ▲                      ▲            │
│           │                      │            │
└───────────┼──────────────────────┼────────────┘
            │                      │
            ▼                      ▼
    ┌───────────────┐      ┌───────────────┐
    │  GitHub Repo  │      │  Google Ads   │
    │  (Next.js)    │      │  API          │
    └───────────────┘      └───────────────┘
```

### Deployment Configuration

The deployment to DigitalOcean App Platform requires specific configuration files:

1. **App Specification File**

```yaml
# .do/app.yaml
name: allervie-dashboard
services:
  - name: web
    github:
      repo: username/allervie-nextjs-clone
      branch: main
    build_command: npm run build
    run_command: npm start
    http_port: 3000
    instance_size: basic-xxs
    instance_count: 1
    routes:
      - path: /
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: ${api.INTERNAL_URL}
        scope: BUILD_TIME
      - key: NODE_ENV
        value: production
        scope: RUN_TIME
      
  - name: api
    github:
      repo: username/allervie-fastapi-backend
      branch: main
    build_command: pip install -r requirements.txt
    run_command: python main.py
    http_port: 5002
    instance_size: basic-xxs
    instance_count: 1
    routes:
      - path: /api
    envs:
      - key: FLASK_ENV
        value: production
        scope: RUN_TIME
      - key: GOOGLE_CLIENT_ID
        value: ${google.client_id}
        type: SECRET
        scope: RUN_TIME
      - key: GOOGLE_CLIENT_SECRET
        value: ${google.client_secret}
        type: SECRET
        scope: RUN_TIME
```

2. **Next.js Configuration**

```javascript
// next.config.js
module.exports = {
  output: 'standalone',  // Optimize for containerized environments
  poweredByHeader: false, // Remove X-Powered-By header for security
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};
```

### Deployment Steps

The deployment process for the Allervie Dashboard to DigitalOcean App Platform follows these steps:

1. **Preparation**:
   - Ensure all environment variables are configured
   - Run build and tests locally to verify functionality
   - Commit and push changes to GitHub

2. **Initial Deployment**:
   - Create a new App in DigitalOcean App Platform
   - Connect to GitHub repository
   - Configure environment variables and resources
   - Deploy the application

### DigitalOcean App Platform Deployment with doctl

In addition to using the DigitalOcean web interface, you can automate the deployment process using the DigitalOcean CLI tool, `doctl`. This approach enables streamlined CI/CD workflows and easier management of deployments.

#### 1. Installing doctl

**For macOS:**
```bash
brew install doctl
```

**For Windows:**
```bash
scoop install doctl
```

**For Linux:**
```bash
sudo snap install doctl
```

Alternatively, you can download the appropriate binary from the [official releases page](https://github.com/digitalocean/doctl/releases).

#### 2. Authenticating with DigitalOcean

```bash
doctl auth init
```

This command will prompt you to enter a personal access token. You can generate one from the DigitalOcean control panel under API > Tokens/Keys.

#### 3. Setting Up App Specification

Create a `.do/app.yaml` file in your project root with the following content:

```yaml
name: allervie-dashboard
region: sfo
services:
  - name: web
    github:
      repo: username/allervie-nextjs-clone
      branch: main
    build_command: npm run build
    run_command: npm start
    http_port: 3000
    instance_size: basic-xxs
    instance_count: 1
    routes:
      - path: /
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: ${api.INTERNAL_URL}
        scope: BUILD_TIME
      - key: NODE_ENV
        value: production
        scope: RUN_TIME
  
  - name: api
    github:
      repo: username/allervie-fastapi-backend
      branch: main
    build_command: pip install -r requirements.txt
    run_command: python main.py
    http_port: 5002
    instance_size: basic-xxs
    instance_count: 1
    routes:
      - path: /api
    envs:
      - key: ENVIRONMENT
        value: production
        scope: RUN_TIME
      - key: GOOGLE_CLIENT_ID
        value: ${google.client_id}
        type: SECRET
        scope: RUN_TIME
      - key: GOOGLE_CLIENT_SECRET
        value: ${google.client_secret}
        type: SECRET
        scope: RUN_TIME
```

Replace `username/allervie-nextjs-clone` and `username/allervie-fastapi-backend` with your actual GitHub repository paths.

#### 4. Creating and Updating Apps

**To create a new app:**
```bash
doctl apps create --spec .do/app.yaml
```

**To update an existing app:**
```bash
doctl apps update APP_ID --spec .do/app.yaml
```

You can get your APP_ID by running `doctl apps list`.

#### 5. Deploying a Specific Component

To deploy a specific component or service within your app:

```bash
doctl apps create-deployment APP_ID --service-name web
```

Replace `web` with the name of the service you want to deploy as defined in your app.yaml file.

#### 6. Automating Deployments with GitHub Actions

Create a GitHub Actions workflow file `.github/workflows/deploy.yml`:

```yaml
name: Deploy to DigitalOcean App Platform

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Deploy app
        run: doctl apps update ${{ secrets.APP_ID }} --spec .do/app.yaml

      - name: Create deployment
        run: doctl apps create-deployment ${{ secrets.APP_ID }}
```

Make sure to add the following secrets to your GitHub repository:
- `DIGITALOCEAN_ACCESS_TOKEN`: Your DigitalOcean personal access token
- `APP_ID`: Your App Platform application ID

#### 7. Monitoring Deployments

**View all deployments:**
```bash
doctl apps list-deployments APP_ID
```

**View detailed deployment information:**
```bash
doctl apps get-deployment APP_ID DEPLOYMENT_ID
```

**View deployment logs:**
```bash
doctl apps logs APP_ID --deployment DEPLOYMENT_ID
```

**View real-time logs:**
```bash
doctl apps logs APP_ID --service-name web --follow
```

Using `doctl` provides powerful command-line control over your DigitalOcean App Platform deployments, enabling more advanced automation and integration with CI/CD workflows.

3. **Continuous Deployment**:
   - Set up GitHub Actions for CI/CD pipeline
   - Configure automatic deployments for main branch

4. **Monitoring and Maintenance**:
   - Set up logging and monitoring
   - Configure alerts for errors and performance issues
   - Implement regular backup and disaster recovery procedures

### Environment Variables

The application requires the following environment variables:

| Variable | Description | Environment |
|----------|-------------|-------------|
| `NEXT_PUBLIC_API_URL` | URL of the FastAPI backend API | Build and Runtime |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Runtime (Secret) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Runtime (Secret) |
| `OAUTH_REDIRECT_URI` | OAuth redirect URI | Runtime |
| `NODE_ENV` | Node.js environment (production/development) | Runtime |

## Future Enhancements

The application is designed to be extensible, with planned enhancements including:

1. **Google Analytics 4 Integration**:
   - User behavior metrics
   - Conversion funnels
   - Audience insights

2. **Advanced Campaign Management**:
   - Budget optimization recommendations
   - A/B test analysis
   - Performance forecasting

3. **Enhanced Visualization**:
   - Interactive charts and graphs
   - Customizable dashboards
   - Data export capabilities

4. **Machine Learning Integration**:
   - Anomaly detection
   - Predictive analytics
   - Automated insights

## Conclusion

The Allervie Dashboard Next.js implementation represents a significant improvement over the original React-based application. By leveraging Next.js's advanced features, the application provides better performance, improved developer experience, and a more robust architecture. The integration with Google Ads API provides valuable insights for marketing teams, with a solid foundation for future enhancements including Google Analytics 4 integration.

The deployment to DigitalOcean App Platform ensures reliable hosting with automatic scaling, continuous deployment, and comprehensive monitoring. The documented architecture and deployment process provide a clear roadmap for future development and maintenance.

## Appendix: Code Samples

### Google Ads API Client

```typescript
// src/lib/google-ads-client.ts
import axios from 'axios';
import { mockAdsPerformance } from './mock-data';

// Interface definitions for the Google Ads API data
export interface MetricWithChange {
  value: number;
  change: number;
}

export interface AdsPerformanceData {
  impressions: MetricWithChange;
  clicks: MetricWithChange;
  conversions: MetricWithChange;
  cost: MetricWithChange;
  clickThroughRate: MetricWithChange;
  conversionRate: MetricWithChange;
  costPerConversion: MetricWithChange;
}

// Create API client with default configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

/**
 * Fetches Google Ads performance data from the API
 */
export async function getAdsPerformance(
  startDate?: string,
  endDate?: string,
  previousPeriod: boolean = true,
  useMockData: boolean = false
): Promise<AdsPerformanceData> {
  console.log('Fetching Google Ads performance data', { 
    startDate, endDate, previousPeriod, useMockData 
  });
  
  if (useMockData) {
    console.log('Using mock Google Ads performance data');
    return mockAdsPerformance;
  }

  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (previousPeriod) params.previous_period = 'true';

  try {
    console.log('Making API request to /api/google-ads/performance', { params });
    
    const response = await api.get('/api/google-ads/performance', { params });
    
    console.log('Successfully fetched Google Ads performance data', {
      metrics: Object.keys(response.data),
      timestamp: new Date().toISOString()
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching Google Ads performance data:', error);
    
    if (axios.isAxiosError(error)) {
      console.error('API response:', error.response?.data);
      console.error('Status code:', error.response?.status);
    }
    
    console.log('Falling back to mock Google Ads performance data');
    return mockAdsPerformance;
  }
}
```

### OAuth Implementation

```typescript
// src/app/api/auth/google/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';

// OAuth configuration
const OAUTH_CONFIG = {
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  redirectUri: process.env.OAUTH_REDIRECT_URI || 'http://localhost:3000/api/auth/callback',
  scopes: [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
  ]
};

export async function GET(request: NextRequest) {
  // Generate a random state parameter to prevent CSRF attacks
  const state = randomBytes(16).toString('hex');
  
  // Store the state in a cookie for validation in the callback
  const cookieOptions = {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 10, // 10 minutes
    path: '/'
  };
  
  // Build the OAuth URL
  const authUrl = new URL('https://accounts.google.com/o/oauth2/auth');
  authUrl.searchParams.append('client_id', OAUTH_CONFIG.clientId);
  authUrl.searchParams.append('redirect_uri', OAUTH_CONFIG.redirectUri);
  authUrl.searchParams.append('response_type', 'code');
  authUrl.searchParams.append('scope', OAUTH_CONFIG.scopes.join(' '));
  authUrl.searchParams.append('access_type', 'offline');
  authUrl.searchParams.append('prompt', 'consent');
  authUrl.searchParams.append('state', state);
  
  console.log('Initiating Google OAuth flow', {
    redirectUri: OAUTH_CONFIG.redirectUri,
    scopes: OAUTH_CONFIG.scopes,
    timestamp: new Date().toISOString()
  });
  
  // Set the cookie and redirect to the OAuth URL
  const response = NextResponse.redirect(authUrl.toString());
  response.cookies.set('oauth_state', state, cookieOptions);
  
  return response;
}
```

### OAuth Callback Handler

```typescript
// src/app/api/auth/callback/route.ts
import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// OAuth configuration (same as in the google route)
const OAUTH_CONFIG = {
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  redirectUri: process.env.OAUTH_REDIRECT_URI || 'http://localhost:3000/api/auth/callback',
  scopes: [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
  ]
};

export async function GET(request: NextRequest) {
  console.log('OAuth callback received');
  
  // Get the authorization code and state from the query parameters
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  
  // Get the state from the cookie
  const cookieState = request.cookies.get('oauth_state')?.value;
  
  // Validate the state parameter to prevent CSRF attacks
  if (!state || state !== cookieState) {
    console.error('OAuth state validation failed', {
      receivedState: state,
      cookieState,
      timestamp: new Date().toISOString()
    });
    
    return NextResponse.json(
      { error: 'Invalid state parameter' },
      { status: 400 }
    );
  }
  
  // Check if the authorization code is present
  if (!code) {
    console.error('OAuth callback missing code parameter');
    
    return NextResponse.json(
      { error: 'Missing authorization code' },
      { status: 400 }
    );
  }
  
  try {
    // Exchange the authorization code for tokens
    console.log('Exchanging authorization code for tokens');
    
    const tokenResponse = await axios.post(
      'https://oauth2.googleapis.com/token',
      {
        code,
        client_id: OAUTH_CONFIG.clientId,
        client_secret: OAUTH_CONFIG.clientSecret,
        redirect_uri: OAUTH_CONFIG.redirectUri,
        grant_type: 'authorization_code'
      }
    );
    
    const { access_token, refresh_token, id_token, expires_in } = tokenResponse.data;
    
    console.log('Successfully obtained tokens', {
      hasAccessToken: !!access_token,
      hasRefreshToken: !!refresh_token,
      hasIdToken: !!id_token,
      expiresIn: expires_in,
      timestamp: new Date().toISOString()
    });
    
    // Store the tokens in cookies
    const cookieOptions = {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/'
    };
    
    // Calculate the expiration time for the access token
    const expirationTime = new Date();
    expirationTime.setSeconds(expirationTime.getSeconds() + expires_in);
    
    // Create the response
    const response = NextResponse.redirect(new URL('/dashboard', request.url));
    
    // Set cookies for the tokens
    response.cookies.set('access_token', access_token, {
      ...cookieOptions,
      expires: expirationTime
    });
    
    if (refresh_token) {
      response.cookies.set('refresh_token', refresh_token, {
        ...cookieOptions,
        maxAge: 30 * 24 * 60 * 60 // 30 days
      });
    }
    
    response.cookies.set('id_token', id_token, {
      ...cookieOptions,
      expires: expirationTime
    });
    
    // Clear the state cookie
    response.cookies.delete('oauth_state');
    
    return response;
  } catch (error) {
    console.error('Error exchanging authorization code for tokens:', error);
    
    // Log error details
    if (axios.isAxiosError(error)) {
      console.error('API response:', error.response?.data);
      console.error('Status code:', error.response?.status);
    }
    
    return NextResponse.json(
      { error: 'Failed to exchange authorization code for tokens' },
      { status: 500 }
    );
  }
}
```

These code samples represent key components of the Allervie Dashboard implementation, demonstrating the Google Ads API integration, OAuth authentication flow, and robust error handling with detailed logging.
