/** @type {import('next').NextConfig} */
const nextConfig = {
    /* config options here */
    output: 'export',
    distDir: "_static",
    images: {
        unoptimized: true
    },
    env: {
        // Environment variables are passed through
        NEXTAUTH_URL: process.env.NEXTAUTH_URL,
        NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
        NEXT_PUBLIC_USE_MOCK_DATA: process.env.NEXT_PUBLIC_USE_MOCK_DATA
    }
}

module.exports = nextConfig
