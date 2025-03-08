# Google Ads API Documentation

This document outlines the available Google Ads API endpoints, their usage, and maintenance procedures.

## API Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/google-ads/performance` | GET | Retrieves overall performance metrics | `start_date`, `end_date`, `previous_period` |
| `/api/google-ads/test-connection` | GET | Tests the Google Ads API connection | None |
| `/api/google-ads/simple-test` | GET | Simpler test for the Google Ads API connection | None |
| `/api/google-ads/campaigns` | GET | Retrieves campaign performance data | `start_date`, `end_date` |
| `/api/google-ads/ad_groups` | GET | Retrieves ad group performance data | `start_date`, `end_date`, `campaign_id` |
| `/api/google-ads/search_terms` | GET | Retrieves search term performance data | `start_date`, `end_date`, `campaign_id` |
| `/api/google-ads/keywords` | GET | Retrieves keyword performance data | `start_date`, `end_date`, `ad_group_id` |
| `/api/google-ads/ads` | GET | Retrieves ad performance data | `start_date`, `end_date`, `ad_group_id` |
| `/api/google-ads/available_endpoints` | GET | Returns a list of available Google Ads API endpoints | None |

## Endpoint Details

### `/api/google-ads/performance`

Returns overall performance metrics across all campaigns.

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format (defaults to 30 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (defaults to yesterday)
- `previous_period` (optional): Boolean to include previous period data for comparison

**Response Format:**
```json
{
  "impressions": {"value": 790594, "change": 0},
  "clicks": {"value": 19404, "change": 0},
  "conversions": {"value": 2878.63, "change": 0},
  "cost": {"value": 94526.66, "change": 0},
  "conversionRate": {"value": 0.177, "change": 0},
  "clickThroughRate": {"value": 0.024, "change": 0},
  "costPerConversion": {"value": 32837.37, "change": 0}
}
```

### `/api/google-ads/campaigns`

Returns performance data for all campaigns.

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Response Format:**
```json
[
  {
    "id": "14308191309",
    "name": "AL-Cullman-Search-ALVH",
    "status": "ENABLED",
    "impressions": 1344,
    "clicks": 140,
    "cost": 894.54,
    "ctr": 10.42
  },
  // Additional campaigns...
]
```

### `/api/google-ads/ad_groups`

Returns performance data for ad groups, optionally filtered by campaign.

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `campaign_id` (optional): Filter by specific campaign ID

**Response Format:**
```json
[
  {
    "id": "144410855677",
    "name": "Adult Onset Allergy - Broad",
    "status": "PAUSED",
    "campaign_id": "14308191309",
    "campaign_name": "AL-Cullman-Search-ALVH",
    "impressions": 0,
    "clicks": 0,
    "cost": 0.0,
    "ctr": 0.0
  },
  // Additional ad groups...
]
```

### `/api/google-ads/search_terms`

Returns performance data for search terms that triggered ads.

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `campaign_id` (optional): Filter by specific campaign ID

**Response Format:**
```json
[
  {
    "search_term": "allergy and asthma center",
    "campaign_id": "20963331348",
    "campaign_name": "MD-Baltimore-Search-Premier",
    "ad_group_id": "157367605399",
    "ad_group_name": "Allergy Treatment",
    "impressions": 572,
    "clicks": 44,
    "cost": 216.66,
    "ctr": 7.69
  },
  // Additional search terms...
]
```

## Maintenance Procedures

### OAuth Token Refresh

The Google Ads API uses OAuth for authentication. The refresh token needs to be updated periodically:

1. Run the refresh token script:
   ```bash
   python backend/get_new_refresh_token.py
   ```

2. Verify the token was updated successfully:
   ```bash
   python backend/test_ads_endpoints.py test
   ```

### API Rate Limits Monitoring

Google Ads API has rate limits that should be monitored:

- Daily quota: 15,000 units
- Queries per minute: 1,800 units
- Queries per day: 86,400 units

To check current usage, run:
```bash
python backend/check_google_ads_quota.py
```

### Troubleshooting Common Issues

1. **Authentication Errors**:
   - Verify the refresh token is valid
   - Check for expired OAuth credentials
   - Run `python backend/diagnose_oauth_error.py`

2. **Missing Data**:
   - Ensure the date range is valid
   - Check if campaigns exist for the specified period
   - Verify the client account has data for the requested metrics

3. **API Changes**:
   - Google occasionally updates the API version
   - Check Google Ads API release notes for changes
   - Update code to use the latest supported version

## MCC Account Configuration

The system is configured to use a client account under an MCC (Manager) account:

- MCC Account ID: 5686645688
- Client Account ID: 8127539892

This configuration is stored in `config.py` and is necessary because the Google Ads API cannot retrieve metrics directly from manager accounts.