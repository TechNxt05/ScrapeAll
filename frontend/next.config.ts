import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config) => {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const path = require('path');
    config.resolve.alias['@'] = path.join(__dirname, '.');
    return config;
  },
};

export default nextConfig;
