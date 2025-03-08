# Google Ads Dashboard Testing Guide

## Prerequisites
- Valid Google Ads API credentials in `google-ads.yaml`
- Active OAuth refresh token
- Access to client account ID 8127539892

## Test Results Summary

**Test Date:** March 8, 2025  
**Status:** All API endpoints functioning correctly with real Google Ads data

| Endpoint | Status | Data Count |
|----------|--------|------------|
| test-connection | ✅ | n/a |
| simple-test | ✅ | n/a |
| performance | ✅ | 7 metrics |
| campaigns | ✅ | 163 campaigns |
| ad_groups | ✅ | 2,951 ad groups |
| keywords | ✅ | 1,000+ search terms |

## Testing Process

### 1. Verify Backend API Functionality
```bash
# Test all Google Ads API endpoints
python test_ads_endpoints.py

# Test specific endpoints
python test_single_ads_endpoint.py simple
python test_single_ads_endpoint.py performance
python test_single_ads_endpoint.py campaigns
python test_single_ads_endpoint.py ad_groups
python test_single_ads_endpoint.py keywords
```

### 2. Dashboard Testing
1. Start the backend server:
   ```bash
   python app.py
   ```

2. Access the dashboard at:
   ```
   http://localhost:5002/ads-dashboard
   ```

3. Verify the following dashboard elements:
   - Campaign performance chart loads with real data
   - Ad performance metrics display correctly
   - Keyword performance data appears in the table
   - Date range selector functions properly
   - All API requests show successful status codes in browser console

### 3. API Response Validation
- Check that all metrics are properly formatted
- Verify that numeric values have appropriate precision
- Ensure date fields follow ISO format (YYYY-MM-DD)
- Confirm API responses include proper headers for CORS

### 4. Authentication Testing
- Verify dashboard handles token expiration gracefully
- Test automatic token refresh functionality
- Ensure proper error messages display if authentication fails

### 5. Edge Cases
- Test with date ranges that have no data
- Verify behavior when API quota is approaching limits
- Check performance with large data sets

## Troubleshooting

If dashboard fails to load data:
1. Check browser console for API errors
2. Verify OAuth token is valid (run `python get_new_refresh_token.py` if needed)
3. Confirm client account ID is correctly set in requests
4. Check Google Ads API quota using `python check_google_ads_quota.py`

## Reporting Issues
Document any issues with:
- Screenshots of the problem
- Browser console logs
- API response data
- Steps to reproduce