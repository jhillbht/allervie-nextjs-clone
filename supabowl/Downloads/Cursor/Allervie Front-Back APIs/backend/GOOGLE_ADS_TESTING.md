# Google Ads API Testing Guide

This document explains how to test the Google Ads API endpoints in the Allervie Analytics Dashboard.

## Available Endpoints

The following Google Ads API endpoints are available for testing:

1. `/api/google-ads/performance` - Overall performance metrics
2. `/api/google-ads/test-connection` - Test the Google Ads API connection
3. `/api/google-ads/simple-test` - Simple connectivity test
4. `/api/google-ads/campaigns` - Campaign performance data
5. `/api/google-ads/ad_groups` - Ad group performance data
6. `/api/google-ads/search_terms` - Search term performance data
7. `/api/google-ads/keywords` - Keyword performance data
8. `/api/google-ads/ads` - Ad performance data
9. `/api/google-ads/available_endpoints` - List of available endpoints

## Testing Scripts

Two testing scripts are provided to help you test the Google Ads API endpoints:

1. `test_ads_endpoints.py` - Tests all Google Ads API endpoints at once
2. `test_single_ads_endpoint.py` - Tests a single endpoint with customizable parameters

### Prerequisites

Before running the tests, make sure:

1. The Allervie Analytics Dashboard server is running on localhost:5002
2. You have properly configured the Google Ads API credentials
3. You have Python and the `requests` library installed:

```bash
pip install requests
```

### Test All Endpoints

To test all Google Ads API endpoints at once, run:

```bash
python backend/test_ads_endpoints.py
```

This will test each endpoint sequentially and provide a summary of the results.

### Test a Single Endpoint

To test a specific endpoint with custom parameters, use:

```bash
python backend/test_single_ads_endpoint.py <endpoint> [options]
```

#### Available Endpoints:

- `test` - Test connection
- `simple` - Simple test
- `performance` - Performance metrics
- `campaigns` - Campaign data
- `ad_groups` - Ad group data
- `search_terms` - Search term data
- `keywords` - Keyword data
- `ads` - Ad data
- `available` - Available endpoints

#### Options:

- `--base-url BASE_URL` - Base URL for the API (default: http://localhost:5002)
- `--param KEY=VALUE` - Additional parameters (can be used multiple times)
- `--verbose`, `-v` - Print the full response data

#### Examples:

Test the performance endpoint:
```bash
python backend/test_single_ads_endpoint.py performance
```

Test the campaigns endpoint with a custom date range:
```bash
python backend/test_single_ads_endpoint.py campaigns --param start_date=2023-01-01 --param end_date=2023-01-31
```

Test the ad_groups endpoint with a specific campaign ID:
```bash
python backend/test_single_ads_endpoint.py ad_groups --param campaign_id=12345678
```

Test the search_terms endpoint with verbose output:
```bash
python backend/test_single_ads_endpoint.py search_terms --verbose
```

## Troubleshooting

If you encounter issues while testing the API endpoints, refer to the `GOOGLE_ADS_TROUBLESHOOTING.md` document for common problems and solutions.

### Common Issues:

1. **Connection Refused**: Make sure the server is running on the correct port
2. **Authentication Errors**: Check your Google Ads API credentials
3. **Missing Data**: Verify that your Google Ads account has data for the requested date range
4. **API Quota Exceeded**: Google Ads API has rate limits, wait a few minutes and try again

## Next Steps

After successfully testing the API endpoints, you can:

1. Integrate the endpoints with your frontend application
2. Create custom visualizations of the Google Ads data
3. Set up automated monitoring of your Google Ads performance