import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',  // Optimize for containerized environments
  poweredByHeader: false, // Remove X-Powered-By header for security
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
