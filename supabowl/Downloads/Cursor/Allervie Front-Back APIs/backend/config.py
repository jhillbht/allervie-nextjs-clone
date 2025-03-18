# Global configuration variables
import os

# Set to True to always attempt to use real Google Ads data
# instead of mock data, even with mock authentication tokens
USE_REAL_ADS_CLIENT = os.environ.get('USE_REAL_ADS_CLIENT', 'true').lower() == 'true'

# Set to True to allow mock data for testing
ALLOW_MOCK_DATA = os.environ.get('ALLOW_MOCK_DATA', 'false').lower() == 'true'

# Set to True to enable mock authentication
ALLOW_MOCK_AUTH = os.environ.get('ALLOW_MOCK_AUTH', 'false').lower() == 'true'

# Set environment (development or production)
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

# This is the customer ID to use for Google Ads API requests
CLIENT_CUSTOMER_ID = os.environ.get('CLIENT_CUSTOMER_ID', '8127539892')
