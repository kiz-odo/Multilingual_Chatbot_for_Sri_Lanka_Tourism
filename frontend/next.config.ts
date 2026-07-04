import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Memory optimization settings
  experimental: {
    // Reduce memory usage during compilation
    webpackMemoryOptimizations: true,
    // Reduce worker threads for lower memory usage
    cpus: 1,
  },

  // Optimize build output
  compress: true,

  // Reduce memory footprint of image optimization
  images: {
    // Allowlist of hosts the app actually serves images from. Avoid a "**"
    // wildcard: it turns the Next image optimizer into an open proxy that will
    // fetch/optimize any URL. Sources: Unsplash (fallbacks in lib/image-utils),
    // Google Places photos (maps.googleapis.com, which redirect to
    // *.googleusercontent.com), and localhost for dev.
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "maps.googleapis.com",
      },
      {
        protocol: "https",
        hostname: "**.googleusercontent.com",
      },
      {
        protocol: "http",
        hostname: "localhost",
      },
    ],
    // Limit concurrent image optimization
    minimumCacheTTL: 60,
    formats: ['image/webp'],
    // Allow unoptimized images in development
    unoptimized: process.env.NODE_ENV === 'development',
  },

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001/ws",
    NEXT_PUBLIC_GA_ID: process.env.NEXT_PUBLIC_GA_ID,
    NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
  },

  // Proxy API requests to backend
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
    return [
      {
        source: "/health/:path*",
        destination: `${backendUrl}/health/:path*`,
      },
      {
        source: "/health",
        destination: `${backendUrl}/health`,
      },
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
      {
        source: "/ws/:path*",
        destination: `${backendUrl}/ws/:path*`,
      },
    ];
  },

  // Output standalone for Docker
  output: 'standalone',
};

export default nextConfig;
