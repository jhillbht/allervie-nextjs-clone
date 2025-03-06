# Google Ads API Troubleshooting Guide

This document provides solutions for common issues you might encounter when setting up and using the Google Ads API with the Allervie Analytics Dashboard.

## Troubleshooting Steps

### Step 1: Check Your YAML Configuration

The most common issues with Google Ads API are related to incorrect configuration in the `google-ads.yaml` file. Use the provided validation script to check your configuration:

```bash
python backend/check_google_ads_yaml.py
```

This script will:
1. Check if all required fields are present
2. Validate the format of your customer ID (it should not contain dashes)
3. Check if you have a refresh token
4. Fix some common issues automatically
5. Provide guidance for manual fixes

### Step 2: Test Basic API Connectivity

If your YAML configuration looks good but you're still having issues, use the basic connectivity test script:

```bash
python backend/test_basic_ads_connection.py
```

This script performs a simple test to verify that your Google Ads API credentials are working correctly. It will provide detailed error messages if the connection fails.

### Step 3: Check Your Developer Token Status

Your developer token status might affect your ability to access the Google Ads API:

1. **Test Token**: If you're using a test token, you might have limited access to the API.
2. **Production Token**: A production token provides full access but requires approval from Google.

To check your token status:
1. Go to your Google Ads account
2. Navigate to Tools & Settings > Setup > API Center
3. Check if your token is approved for production access

### Step 4: Verify Customer ID Access

Make sure the customer ID you're using:
1. Is a valid Google Ads account ID
2. Is an account you have access to
3. Is formatted correctly (10 digits with no dashes)

If you're using a manager account (MCC), you might need to specify child account IDs for certain operations.

### Step 5: Check OAuth Scopes

The OAuth scopes you requested during authentication must include the Google Ads API scope:

```
https://www.googleapis.com/auth/adwords
```

If you didn't request this scope, you'll need to generate a new refresh token with the correct scopes:

```bash
python backend/get_refresh_token.py
```

### Step 6: Debug API Requests and Responses

If you're still having issues, enable detailed logging to see the exact requests and responses:

1. Edit `backend/google_ads_client.py` to increase the logging level:
   ```python
   googleads_logger.setLevel(logging.DEBUG)
   ```

2. Run your application and check the console for detailed logs

## Common Error Messages and Solutions

### "Authentication error"

**Possible causes:**
- Invalid client ID or client secret
- Expired refresh token
- Missing or incorrect OAuth scopes

**Solutions:**
1. Verify your client ID and client secret in `google-ads.yaml`
2. Generate a new refresh token using `backend/get_refresh_token.py`
3. Make sure your OAuth consent screen has the "AdWords" scope

### "Customer not found"

**Possible causes:**
- Invalid customer ID
- Customer ID contains dashes
- You don't have access to this customer account

**Solutions:**
1. Verify your customer ID in Google Ads UI
2. Remove dashes from the customer ID in `google-ads.yaml`
3. Make sure you have access to this account in Google Ads

### "Developer token not approved"

**Possible causes:**
- Your developer token is in test mode
- Your developer token has not been approved for production access

**Solutions:**
1. For testing, use a Google Ads test account
2. Apply for production access through the Google Ads API Center
3. Use only API features that are available with test tokens

### "Access denied to the resource"

**Possible causes:**
- Insufficient permissions
- Wrong customer ID
- API access not enabled for this account

**Solutions:**
1. Check your account permissions in Google Ads
2. Verify you're using the correct customer ID
3. Enable API access for this account in Google Ads

## Additional Resources

- [Google Ads API Client Library for Python Documentation](https://developers.google.com/google-ads/api/docs/client-libs/python)
- [Google Ads API Error Codes](https://developers.google.com/google-ads/api/reference/rpc/v14/GoogleAdsFailure)
- [OAuth 2.0 for Google APIs](https://developers.google.com/identity/protocols/oauth2)
- [Getting Started with Google Ads API](https://developers.google.com/google-ads/api/docs/start)

## Getting Help

If you continue to experience issues after following these troubleshooting steps, you can:

1. Check the Google Ads API Forum: https://groups.google.com/g/adwords-api
2. Search for similar issues on Stack Overflow with the tag [google-ads-api]
3. Review the Google Ads API release notes for any known issues
