import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbo: {
    resolveAlias: {
      '@': './',
    },
  },
};

export default nextConfig;
