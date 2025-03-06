# Allervie Analytics Dashboard

This project implements a full-stack analytics dashboard for Allervie, featuring real-time data from Google Ads API and Google Analytics. The dashboard provides comprehensive metrics, campaign analysis, ad group performance, and search terms reports, all within a responsive and user-friendly interface.

## Features

- **Real-time Google Ads Data**: Connects directly to Google Ads API to fetch current campaign performance metrics
- **Enhanced Campaign Analytics**: View detailed performance by campaign, ad group, and search term
- **Interactive Visualizations**: Charts and graphs that visualize key performance indicators
- **Date Range Filtering**: Filter data by custom date ranges
- **Campaign Filtering**: Focus on specific campaigns for detailed analysis
- **Responsive UI**: Based on Material UI for a modern, responsive design
- **Secure Authentication**: OAuth integration for secure access to analytics data
- **Improved Google Ads Integration**: Enhanced error handling and token management for more reliable API connections

## Architecture

The application follows a client-server architecture:

### Backend (Flask API)
- **Authentication Service**: Handles Google OAuth authentication flow
- **Analytics APIs**: Provides endpoints for dashboard data
- **Google Ads Integration**: Real-time connection to Google Ads API with improved error handling
- **Smart Token Management**: Automated refresh token handling and credential validation
- **Enhanced Routes**: Additional endpoints for detailed campaign data

### Frontend (React)
- **Authentication Layer**: Manages user authentication state
- **UI Components**: Reusable dashboard components with Material UI
- **API Client**: Communicates with the backend
- **Enhanced Google Ads Component**: Specialized component for Google Ads data visualization

## Requirements

- Python 3.8+
- Node.js 14+
- Google Ads API credentials
- Google Analytics API credentials

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Google Ads API credentials:
   - Place your `google-ads.yaml` file in the `credentials` directory
   - Ensure it contains the correct `developer_token`, `client_id`, `client_secret`, `refresh_token`, and `login_customer_id`

4. Configure your Google OAuth credentials:
   - Place your `client_secret.json` in the `credentials` directory

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install NPM dependencies:
   ```bash
   npm install
   ```

## Running the Application

You can run both the backend and frontend with a single command using the provided test script:

```bash
./run_test.py
```

This script will:
1. Test the Google Ads API connection
2. Start the Flask backend server
3. Start the React frontend development server
4. Open a browser to view the dashboard

Alternatively, you can run the components separately:

### Backend

```bash
cd backend
python app.py
```

The backend will run on http://localhost:5001

### Frontend

```bash
cd frontend
npm start
```

The frontend will run on http://localhost:3000

## Testing the Google Ads API

To specifically test the Google Ads API integration:

```bash
cd backend
python test_google_ads_api.py
```

This will run a series of tests to verify connectivity with the Google Ads API and display sample data from your account.

## API Endpoints

### Authentication Endpoints

- **GET /api/auth/login**: Initiates the OAuth flow
- **GET /api/auth/callback**: Handles the OAuth callback
- **GET /api/auth/verify**: Verifies token validity

### Google Ads API Endpoints

- **GET /api/google-ads/performance**: Returns Google Ads performance metrics
- **GET /api/google-ads/campaigns**: Returns detailed campaign performance data
- **GET /api/google-ads/ad_groups**: Returns ad group performance data
- **GET /api/google-ads/search_terms**: Returns search terms report

### Dashboard Data Endpoints

- **GET /api/dashboard/summary**: Returns dashboard summary data
- **GET /api/form-performance**: Returns form performance statistics
- **GET /api/site-metrics**: Returns site metrics
- **GET /api/performance-over-time**: Returns time series data for charts

## Security Considerations

- Token-based authentication using JWT
- CORS protection for API endpoints
- Environment variables for sensitive information
- Protected routes with authentication checks

## Documentation

For detailed instructions on setting up and troubleshooting the Google Ads integration, refer to these guides:

- [Google Ads Setup Guide](GOOGLE_ADS_SETUP.md): Step-by-step instructions for setting up Google Ads API integration
- [Google Ads Troubleshooting Guide](GOOGLE_ADS_TROUBLESHOOTING.md): Solutions for common integration issues

## Troubleshooting

If you encounter issues with the Google Ads API connection:

1. Verify that your `google-ads.yaml` file contains valid credentials
2. Ensure that API access is enabled in your Google Ads account
3. Check that your developer token is approved for the requested API version
4. Verify that the login customer ID has the correct permissions
5. Use the diagnostic tools in `backend/diagnose_oauth_error.py` to troubleshoot authentication issues

For OAuth authentication issues:

1. Ensure your `client_secret.json` is correctly configured
2. Verify that the redirect URI matches the one configured in your Google Cloud Console
3. Check that the required scopes are enabled for your OAuth application
4. Use the `get_new_refresh_token.py` script if your refresh token needs to be updated

## Future Enhancements

- User management and role-based access control
- Additional data visualizations and report types
- Export functionality for PDF and CSV
- Real-time data updates using WebSockets
- Mobile app integration

## License

This project is proprietary and confidential.
