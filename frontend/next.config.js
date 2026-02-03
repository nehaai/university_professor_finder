/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output standalone for optimized production builds
  output: 'standalone',

  // Environment variables that will be available at build time
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://uni-prof-finder-production.up.railway.app',
  },
};

module.exports = nextConfig;
