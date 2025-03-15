# Allervie Dashboard Next.js Implementation Guide

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

## DigitalOcean Deployment

### Deployment Configuration

1. Create `.do/app.yaml` in the root directory:
   ```yaml
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
   ```

2. Configure DigitalOcean App Platform:
   - Connect GitHub repository
   - Set environment variables
   - Deploy application

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
