# Setting Up Google Ads API Integration

This document provides instructions for setting up and using the Google Ads API integration with the Allervie Analytics Dashboard.

## Prerequisites

1. **Google Cloud Platform (GCP) Project**
   - A Google Cloud Platform project with the Google Ads API enabled
   - OAuth 2.0 client credentials (client ID and client secret)

2. **Google Ads Account**
   - Access to a Google Ads account
   - A developer token for the Google Ads API

3. **Manager Account (MCC) Access**
   - Access to a Google Ads Manager Account (for agencies)
   - Or direct access to a Google Ads account

## Setup Instructions

### 1. Install Required Dependencies

The Google Ads API client library has been added to the `requirements.txt` file. You can install it by running:

```bash
pip install -r backend/requirements.txt
```

### 2. Configure Google Ads API Credentials

The Google Ads API requires credentials to be stored in a `google-ads.yaml` file. This file has been created for you at `/credentials/google-ads.yaml` with the following structure:

```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID
client_secret: YOUR_CLIENT_SECRET
login_customer_id: YOUR_CUSTOMER_ID
use_proto_plus: True
refresh_token: YOUR_REFRESH_TOKEN
```

The credentials have been filled in based on the values from your `.env` file:

- `GOOGLE_ADS_DEVELOPER_TOKEN` from `.env` is used for the `developer_token`
- `CLIENT_ID` from `.env` is used for the `client_id`
- `CLIENT_SECRET` from `.env` is used for the `client_secret`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID` from `.env` is used for the `login_customer_id`

### 3. Generate a Refresh Token

To use the Google Ads API, you need to generate a refresh token. A script has been created to help you with this process:

```bash
python backend/get_refresh_token.py
```

This script will:
1. Open a browser window for you to authenticate with Google
2. Request the necessary OAuth scopes for Google Ads API access
3. Receive the authorization code and exchange it for tokens
4. Update the `google-ads.yaml` file with the refresh token

Alternatively, if you already have a refresh token, you can update the YAML file directly with:

```bash
python backend/get_refresh_token.py --update-only --refresh-token YOUR_REFRESH_TOKEN
```

### 4. Test Your Google Ads API Connection

A test script has been created to verify your Google Ads API connection. You can run it with:

```bash
./test_google_ads_setup.sh
```

This script will:
1. Create a virtual environment if it doesn't exist
2. Install the required dependencies
3. Run a test script to verify the Google Ads API connection
4. Provide feedback on success or failure

### 5. Using Real Google Ads Data

The application is now configured to use real Google Ads data when available. The `/api/google-ads/performance` endpoint will:

1. Try to fetch real data from the Google Ads API
2. Fall back to mock data if the API request fails

You can control the date range by providing query parameters:
- `start_date`: Start date in YYYY-MM-DD format (defaults to 7 days ago)
- `end_date`: End date in YYYY-MM-DD format (defaults to yesterday)

Example:
```
GET /api/google-ads/performance?start_date=2024-02-01&end_date=2024-02-15
```

## Troubleshooting

If you encounter issues with the Google Ads API connection, check the following:

1. **Developer Token**: Ensure your developer token is valid and approved by Google
2. **Customer ID Format**: The customer ID should be the 10-digit ID without dashes
3. **OAuth Scopes**: Ensure your OAuth consent screen includes the AdWords scope
4. **API Access**: Verify that your account has access to the Google Ads API

Common error messages:

- `AUTHENTICATION_ERROR`: Check your client ID, client secret, and refresh token
- `DEVELOPER_TOKEN_PARAMETER_MISSING`: Developer token is missing from the request
- `DEVELOPER_TOKEN_NOT_APPROVED`: Developer token is not approved for production access
- `CUSTOMER_NOT_FOUND`: The specified customer ID does not exist or you don't have access

## Resources

- [Google Ads API Client Library for Python](https://developers.google.com/google-ads/api/docs/client-libs/python)
- [Google Ads API Developer Token Request](https://developers.google.com/google-ads/api/docs/first-call/dev-token)
- [Google Ads API Authentication](https://developers.google.com/google-ads/api/docs/oauth/overview)
