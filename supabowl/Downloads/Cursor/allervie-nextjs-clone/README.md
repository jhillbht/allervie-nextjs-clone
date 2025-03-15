# Allervie Dashboard - Next.js Version

This is a Next.js rebuild of the Allervie Analytics Dashboard, focusing first on Google Ads API integration with plans to add Google Analytics 4 (GA4) data later.

## Features

- Google Ads API integration
- Real-time performance metrics
- Campaign performance tracking
- Responsive design using Tailwind CSS
- Server-side data fetching with client-side hydration
- Fallback to mock data when API is unavailable

## Technology Stack

- Next.js 15 with App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Chart.js / React-Chartjs-2
- Axios for API requests
- date-fns for date handling

## Getting Started

### Prerequisites

- Node.js 18.x or later
- Google Ads API access and credentials

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd allervie-nextjs-clone
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.local.example` to `.env.local`
   - Update the variables with your API URLs and configuration

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Backend API Integration

The dashboard connects to a Flask backend API for Google Ads data. The backend should be running on `http://localhost:5002` by default, but this can be configured in the `.env.local` file.

### Environment Variables

- `NEXT_PUBLIC_API_URL`: URL of the backend API
- `NEXT_PUBLIC_USE_MOCK_DATA`: Whether to use mock data instead of real API data (true/false)

## Available Scripts

- `npm run dev`: Starts the development server
- `npm run build`: Builds the app for production
- `npm run start`: Starts the production server
- `npm run lint`: Runs ESLint

## Deployment

This application can be deployed to any platform that supports Next.js applications, such as Vercel, Netlify, or DigitalOcean App Platform.

## Google Ads API Setup

To use the Google Ads API, you need to:

1. Create a Google Cloud Platform project
2. Enable the Google Ads API
3. Create OAuth credentials
4. Generate a refresh token
5. Configure the backend API with your credentials

See the Google Ads API documentation for more details.

## Future Enhancements

- Google Analytics 4 (GA4) integration
- Extended campaign management
- Ad group and keyword performance tracking
- Custom date range selection
- Data export capabilities
- User authentication and personalization
