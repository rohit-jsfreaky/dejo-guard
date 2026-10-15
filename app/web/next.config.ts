import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // our CSS is small: inlining it removes a render-blocking request for first-time visitors
  experimental: { inlineCss: true },
};

export default nextConfig;
