import { NextResponse } from 'next/server';

export async function GET() {
  // Check for required environment variables
  const requiredEnvVars = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NODE_ENV: process.env.NODE_ENV,
    // Add other required environment variables here
  };

  const missingEnvVars = Object.entries(requiredEnvVars)
    .filter(([_, value]) => !value)
    .map(([key]) => key);

  return NextResponse.json({
    status: missingEnvVars.length > 0 ? 'warning' : 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV,
    config: {
      apiUrl: process.env.NEXT_PUBLIC_API_URL,
      missingVariables: missingEnvVars.length > 0 ? missingEnvVars : null,
    }
  });
}