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
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "**",
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
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    NEXT_PUBLIC_GA_ID: process.env.NEXT_PUBLIC_GA_ID,
    NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
  },
  
  // Output standalone for Docker
  output: 'standalone',
};

export default nextConfig;
