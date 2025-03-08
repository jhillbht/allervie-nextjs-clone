# Allervie Analytics Dashboard Development Guide

## Key Commands
- Backend server: `cd backend && python app.py`
- Test Google Ads API: `python backend/test_ads_endpoints.py`
- Test single endpoint: `python backend/test_single_ads_endpoint.py [endpoint] [options]`
- Validate Ads config: `python backend/check_google_ads_yaml.py`
- Refresh OAuth token: `python backend/get_new_refresh_token.py`

## Code Style Guidelines
- **Python**: Follow PEP 8, use type hints, docstrings for all functions
- **Error handling**: Always use try/except blocks with specific error types
- **Imports**: Group standard library, third-party, and local imports
- **Logging**: Use the logging module instead of print statements
- **API responses**: Consistent format with status code, message, and data
- **Naming**: snake_case for Python, camelCase for JavaScript
- **Functions**: Single responsibility, descriptive names, max 30 lines

## Common Project Structure
- API endpoint definitions in `backend/app.py` and `backend/extended_routes.py`
- Google Ads API integration in `backend/extended_google_ads_api.py`
- Configuration settings in `backend/config.py`