# Using Real OAuth Tokens with Allervie Dashboard

This guide explains how to set up and use real Google OAuth tokens with the Allervie Dashboard for accessing the Google Ads API.

## Prerequisites

Before you begin, make sure you have:

1. A Google account with access to Google Ads
2. The proper OAuth client credentials in your `client_secret.json` file
3. The Google Ads Developer Token in your `google-ads.yaml` file

## Getting a Real OAuth Token

To get a real OAuth token, follow these steps:

1. Run the OAuth token generator script:

```bash
./get_real_token.sh
```

2. The script will:
   - Start a local OAuth server on port 49153
   - Open your browser to authenticate with Google
   - Obtain a real OAuth token with the necessary scopes
   - Update your `google-ads.yaml` file with the new refresh token

3. Follow the prompts in your browser to authenticate with Google and grant the necessary permissions.

4. When you see "Authentication Successful!" in your browser, return to the terminal.

## Starting the Production Server

After obtaining a real OAuth token:

1. Run the production server:

```bash
./run_production.sh
```

2. The server will start in production mode with:
   - All mock data completely removed
   - All mock authentication disabled
   - Real Google Ads API data only

## Testing the Google Ads API Endpoints

### Using Python

```python
import requests

# Replace with your real OAuth token
auth_token = "YOUR_REAL_OAUTH_TOKEN"

# Test the performance endpoint
response = requests.get(
    "http://localhost:5002/api/google-ads/performance",
    headers={"Authorization": f"Bearer {auth_token}"}
)

print(response.json())
```

### Using the Command Line

```bash
# Replace with your real OAuth token
AUTH_TOKEN="YOUR_REAL_OAUTH_TOKEN"

# Test the performance endpoint
python -c "import requests; response = requests.get('http://localhost:5002/api/google-ads/performance', headers={'Authorization': 'Bearer $AUTH_TOKEN'}); print(response.json())"
```

## Troubleshooting

If you encounter issues:

1. **Authentication Errors**:
   - Ensure your `client_secret.json` is valid and has the correct redirect URIs
   - Check that your Google account has access to the Google Ads account

2. **API Errors**:
   - Verify that your `google-ads.yaml` has a valid refresh token
   - Make sure your Developer Token is valid
   - Confirm that the `login_customer_id` in `google-ads.yaml` is correct

3. **No Data Returned**:
   - Check if your Google Ads account has any active campaigns
   - Verify that the date range you're querying has data