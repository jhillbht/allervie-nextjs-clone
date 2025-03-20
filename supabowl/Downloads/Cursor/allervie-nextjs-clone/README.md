# Allervie Analytics Dashboard

A Next.js dashboard for Allervie Health's marketing analytics, featuring Google Ads API integration.

## Context Priming
Read README.md, CLAUDE.md, ai_docs/*, and run git ls-files to understand codebase.

Keep troubleshooting the deployment and make memory checkpoints.

Feel free to update the CLAUDE.md, and README, and look for areas to share context via doctl.

Create a detailed Technical Summary of current Project Knowledge as a markdown file.

Create a graphical representation of the current project "Rebuild with Next.js" as an artifact.

## Features

- Real-time Google Ads performance metrics visualization
- Campaign performance tracking and analysis
- Responsive design for all device sizes
- OAuth authentication with Google
- API routes for backend functionality

## Technology Stack

- Next.js 15.2+
- TypeScript
- Tailwind CSS
- Chart.js for data visualization
- Deployed on DigitalOcean App Platform

## Getting Started

### Prerequisites

- Node.js 22.x
- npm or pnpm
- Google Ads API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/allervie-nextjs-clone.git
   cd allervie-nextjs-clone
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   pnpm install
   ```

3. Create a `.env.local` file with the following variables:
   ```
   # Authentication
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your_nextauth_secret
   
   # Google API
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   
   # API URL
   NEXT_PUBLIC_API_URL=http://localhost:3000
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment

### Deploy to DigitalOcean App Platform

1. Install the doctl CLI:
   ```bash
   # On macOS
   brew install doctl
   
   # On Linux
   snap install doctl
   ```

2. Authenticate with DigitalOcean:
   ```bash
   doctl auth init
   ```

3. Run the deployment script:
   ```bash
   ./deploy-digitalocean.sh
   ```

4. Monitor the deployment:
   ```bash
   node scripts/monitor-deployment.js APP_ID
   ```

### Environment Variables for Production

Make sure to set the following environment variables in your DigitalOcean App Platform settings:

- `NEXTAUTH_URL` - The URL of your deployed application
- `NEXTAUTH_SECRET` - A secret for NextAuth.js
- `GOOGLE_CLIENT_ID` - Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret
- `NEXT_PUBLIC_API_URL` - The API URL (same as your application URL)
- `NODE_ENV` - Set to `production`

## License

[MIT](LICENSE)
