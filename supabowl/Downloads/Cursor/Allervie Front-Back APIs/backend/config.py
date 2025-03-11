# Global configuration variables

# Set to True to always attempt to use real Google Ads data
# instead of mock data, even with mock authentication tokens
USE_REAL_ADS_CLIENT = True

# Set to False to force real data only (no mock data fallback)
ALLOW_MOCK_DATA = False  # Force real Google Ads data only

# Set to False to disable mock authentication
ALLOW_MOCK_AUTH = False  # Force real Google Ads authentication

# Set environment (development or production)
ENVIRONMENT = "production"  # Using production mode for reliable API connections

# This is the customer ID to use for Google Ads API requests
CLIENT_CUSTOMER_ID = "8127539892"
