# Allervie Analytics Dashboard Development Guide

## Key Commands
- Start backend server: `cd backend && python app.py`
- Restart backend server: `pkill -f "python backend/app.py" && cd backend && python app.py`
- Test Google Ads API integration: `python backend/test_ads_connection.py`
- Test specific API endpoint: `python backend/test_single_ads_endpoint.py [endpoint] [options]`
  - Available endpoints: campaigns, ad_groups, search_terms, keywords, ads, performance
  - Example: `python backend/test_single_ads_endpoint.py campaigns start_date=2025-02-01 end_date=2025-03-01`
- Validate Google Ads config: `python backend/check_google_ads_yaml.py`
- Refresh OAuth tokens: `python backend/get_new_refresh_token.py`
- Verify API quota usage: `python backend/check_google_ads_quota.py`
- Test refresh functionality: `python backend/test_ads_refresh.py --all`

## Code Style Guidelines
- **Python**: Follow PEP 8, use type hints, and include docstrings for all functions and modules
- **Error handling**: Use specific exceptions in try/except blocks with detailed error messages
- **Imports**: Group imports: standard library → third-party → local (alphabetically within each group)
- **Logging**: Use the logging module with appropriate levels (info, warning, error) instead of print statements
- **API responses**: Return consistent JSON format with status, message, and data fields
- **Naming conventions**: snake_case for Python variables/functions, camelCase for JavaScript
- **Functions**: Keep functions focused on a single responsibility, descriptive names, under 30 lines
- **Security**: Never commit credentials or tokens; use environment variables or yaml configs

## Project Structure
- Main API and server: `backend/app.py`
- Extended Google Ads endpoints: `backend/extended_routes.py`
- Google Ads API integration: `backend/extended_google_ads_api.py` and `backend/google_ads_client.py`
- Mock data fallbacks: `backend/google_ads_fallback.py`
- Configuration settings: `backend/config.py` (environment, feature flags, API settings)
- Frontend templates: `backend/templates/*.html`

## Testing with Real Google Ads API Data (Default)

The dashboard is configured to use real Google Ads API data by default for both development and production.

### Quick Testing Setup

1. Ensure `google-ads.yaml` is properly configured in the `/backend/` directory:
   ```yaml
   client_id: YOUR_CLIENT_ID
   client_secret: YOUR_CLIENT_SECRET
   developer_token: YOUR_DEVELOPER_TOKEN
   login_customer_id: YOUR_CUSTOMER_ID
   refresh_token: YOUR_REFRESH_TOKEN
   use_proto_plus: true
   api_version: v17
   ```

2. Test connection with a single command:
   ```bash
   python backend/test_ads_connection.py
   ```

3. Start dashboard and access immediately:
   ```bash
   cd backend && python app.py
   # Open browser to http://localhost:5002/ads-dashboard
   ```

### OAuth Setup (Only needed for new credentials)
1. Run `python backend/get_new_refresh_token.py`
2. Follow browser prompts to authenticate with Google account
3. Add the new refresh_token to your `google-ads.yaml` file

### Targeted Testing
- Test specific endpoint: `python backend/test_single_ads_endpoint.py campaigns`
- Debug API issues: `python backend/diagnose_oauth_error.py`
- View raw API response structure: `python backend/test_google_ads_direct.py`

### Troubleshooting
- Verify YAML configuration: `python backend/check_google_ads_yaml.py`
- Check API version compatibility (v14-v17 supported)
- Error logs are saved to `app.log` in backend directory
- In rare cases when real data fails, set `ALLOW_MOCK_DATA = True` temporarily in config.py

## Deployment to DigitalOcean App Platform

### Prerequisites
1. DigitalOcean account with App Platform access
2. doctl CLI tool installed and authenticated

### Deployment Steps
1. Prepare app for deployment:
   ```bash
   # Create app.yaml for DigitalOcean App Platform
   cat > app.yaml << EOL
   name: allervie-analytics-dashboard
   services:
   - name: api
     github:
       branch: main
       repo: yourusername/allervie-analytics
     envs:
     - key: FLASK_APP
       value: backend/app.py
     - key: FLASK_ENV
       value: production
     - key: ALLOW_MOCK_DATA
       value: "false"
     - key: GOOGLE_ADS_YAML
       type: SECRET
   EOL
   ```

2. Add secrets for Google Ads API:
   ```bash
   # Encode google-ads.yaml as base64 and add as secret
   base64 -i backend/google-ads.yaml | doctl apps create-secret allervie-analytics-dashboard --key GOOGLE_ADS_YAML --value-file -
   ```

3. Deploy app:
   ```bash
   doctl apps create --spec app.yaml
   ```

4. Configure custom domain (optional):
   ```bash
   doctl apps create-domain allervie-analytics-dashboard --domain dashboard.allervie.com
   ```

5. Monitor deployment:
   ```bash
   doctl apps get allervie-analytics-dashboard
   ```

### Deployment Considerations
- Scale app as needed in DigitalOcean dashboard
- Set up monitoring alerts for API errors
- Update environment variables through DigitalOcean dashboard
- Configure single dyno for development, multiple for production
- Enable automatic deploys from main branch

## Environment Configuration
- Default mode uses only real Google Ads API data for reliability
- System behavior is controlled in `config.py`:
  - `USE_REAL_ADS_CLIENT = True` (Always use real client when possible)
  - `ALLOW_MOCK_DATA = False` (Default: don't use mock data)
  - `ENVIRONMENT = "production"` (Use strict error handling)