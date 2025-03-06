# Setting Up Google Ads API for Manager (MCC) Accounts

This guide explains how to set up the Allervie Dashboard to work with a Google Ads Manager (MCC) account.

## Background

When using Google Ads API with a Manager account (My Client Center), there is a specific limitation:

> You cannot request metrics directly from a manager account. You must query each client account individually.

If you try to request metrics directly from the manager account, you'll get an error like:

```
Metrics cannot be requested for a manager account. To retrieve metrics, issue separate requests against each client account under the manager account.
```

## Solution

To fix this issue, we provide a script that:

1. Finds all client accounts accessible from your manager account
2. Tests each client account to find a valid one for metrics
3. Updates your `google-ads.yaml` configuration to use this client account

## Step 1: Run the MCC Fix Script

```bash
python backend/fix_google_ads_for_mcc.py
```

This script will:
- Identify accessible client accounts
- Find a valid client account that can be queried for metrics
- Update your configuration while backing up the original

## Step 2: Run the Dashboard with Real Ads Data

After updating the configuration, start the dashboard with:

```bash
./run_with_real_ads.sh
```

This will:
- Start the backend server with real data
- Open the API test page in your browser

## Troubleshooting

If you encounter issues:

- Check if the client account selected has data for the date range you're querying
- Make sure the client account has permission to access ads data
- Look at the logs for detailed error messages
- Restore the original configuration from the backup (google-ads.yaml.bak)

## Technical Details

### Google Ads API Configuration

The `google-ads.yaml` file must have `login_customer_id` set to a valid client account, not a manager account.

### API Calls

When making Google Ads API calls:
1. The `login_customer_id` in the YAML specifies the client account to use
2. The `customer_id` parameter in API calls specifies the actual account to query

For more information, visit the [Google Ads API documentation](https://developers.google.com/google-ads/api/docs/concepts/call-structure).