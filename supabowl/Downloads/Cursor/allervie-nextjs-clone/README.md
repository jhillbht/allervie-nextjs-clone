# Allervie Analytics Dashboard

A simple Next.js application for the Allervie Analytics Dashboard, optimized for deployment on DigitalOcean App Platform.

## Deployment Instructions

### Prerequisites

- Install [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/)
- Authenticate with DigitalOcean: `doctl auth init`

### Deploy with Script

Run the deployment script:

```bash
./deploy.sh
```

This will:
1. Check if doctl is installed and authenticated
2. Check if the app already exists
3. Create or update the app using the configuration in `.do/app.yaml`

### Manual Deployment

1. Create or update the app:

```bash
# For a new app
doctl apps create --spec .do/app.yaml

# For an existing app
doctl apps update APP_ID --spec .do/app.yaml
```

2. Monitor the deployment:

```bash
doctl apps list-deployments APP_ID
```

3. View logs:

```bash
doctl apps logs APP_ID
```

## Development

To run the app locally:

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev
```

## Building

```bash
pnpm build
```

## Running in Production

```bash
pnpm start
```
