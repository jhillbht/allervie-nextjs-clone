# Budget Allocation MCP Server

A sophisticated budget allocation and financial tracking system built as an MCP server. This system provides real-time budget tracking, financial insights, and achievement-based gamification to make financial management more engaging and effective.

## Features

- Financial transaction tracking and categorization
- Budget allocation and monitoring
- Achievement system for financial goals
- Real-time notifications via macOS
- QuickBooks integration
- Banking API integration
- Performance metrics and insights

## Project Structure

```
budget_allocation_mcp/
├── src/
│   ├── financial/       # Core financial engine
│   ├── achievements/    # Achievement system
│   ├── metrics/         # Performance metrics
│   ├── notifications/   # Notification system
│   └── integrations/    # External integrations
├── tests/              # Test suite
├── config/             # Configuration files
├── requirements.txt    # Python dependencies
└── .env.template       # Environment variables template
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

4. Configure your environment variables in `.env`

5. Run the server:
   ```bash
   python src/server.py
   ```

## Configuration

The system requires several environment variables to be configured:

- Database configuration
- QuickBooks API credentials
- Banking API credentials
- Notification settings
- Achievement system settings
- Logging configuration

See `.env.template` for all required variables.

## API Endpoints

- `/health` - Health check endpoint
- `/` - Root endpoint with server information
- `/achievements` - List all available achievements
- `/achievements/{user_id}` - Get achievements for a specific user

Additional endpoints will be documented as they are implemented.

## Achievement System

The system includes a comprehensive achievement and gamification framework to make financial management more engaging:

### Achievement Categories

- **Budget**: Rewards for successful budget management
- **Saving**: Rewards for reaching savings goals
- **Consistency**: Rewards for maintaining good financial habits
- **Milestone**: Rewards for reaching significant financial milestones
- **Challenge**: Special challenge-based achievements
- **System**: System usage rewards

### Achievement Tiers

Each achievement comes in different tiers with increasing rewards:

- Bronze: Entry-level achievements
- Silver: Intermediate achievements
- Gold: Advanced achievements
- Platinum: Expert-level achievements

### Reward Types

The system supports multiple reward types:

- **Points**: Achievement points that accumulate
- **Badges**: Collectible badges for profile display
- **Feature Unlocks**: Access to premium features based on achievements

### Progress Tracking

The achievement system tracks different types of progress:

- **Counter**: Simple numeric counters (e.g., number of transactions)
- **Percentage**: Progress toward a goal (e.g., savings target)
- **Boolean**: Simple completion flags (e.g., linked an account)
- **Streak**: Consecutive completion tracking (e.g., under budget for 3 months)

## Development

For development:

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black .
   isort .
   ```

4. Run linting:
   ```bash
   flake8
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT

## Support

For support, please open an issue in the GitHub repository.