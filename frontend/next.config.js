/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output standalone for optimized production builds
  output: 'standalone',

  // Environment variables that will be available at build time
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig;
