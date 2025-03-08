# Global configuration variables

# Set to True to always attempt to use real Google Ads data
# instead of mock data, even with mock authentication tokens
USE_REAL_ADS_CLIENT = True

# Set to False to disable all mock data functionality
ALLOW_MOCK_DATA = False

# Set to False to disable mock authentication tokens
ALLOW_MOCK_AUTH = False

# Set environment (development or production)
ENVIRONMENT = "production"

# Google Ads API specific settings
# MCC account ID
MANAGER_CUSTOMER_ID = "5686645688"
# Client account ID that we want to retrieve metrics for
CLIENT_CUSTOMER_ID = "8127539892"
