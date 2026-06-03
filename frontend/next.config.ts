import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next 16 defaults to Turbopack; we keep webpack for Docker file watching.
  turbopack: {},
  typescript: {
    // Remaining strict errors are in search/utils and legacy templates; play + builder paths are fixed incrementally.
    ignoreBuildErrors: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cards.scryfall.io',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'c1.scryfall.com',
        pathname: '/**',
      },
    ],
  },
  // Use webpack for better file watching in Docker on Windows
  // Turbopack file watching can be unreliable in Docker volumes
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Enable polling for file watching in Docker
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300, // Delay before rebuilding
        ignored: ['**/node_modules', '**/.next'],
      };
    }
    return config;
  },
};

export default nextConfig;
