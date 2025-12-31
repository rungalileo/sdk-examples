/** @type {import('next').NextConfig} */
const nextConfig = {
  // Webpack configuration for handling problematic packages (Galileo SDK)
  webpack: (config, { isServer }) => {
    if (isServer) {
      // Don't bundle these packages on the server
      config.externals = config.externals || [];
      config.externals.push({
        galileo: "commonjs galileo",
        openai: "commonjs openai",
      });
    }
    return config;
  },

  // Allow embedding in iframes (for Google Colab)
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // Remove X-Frame-Options to allow iframe embedding
          {
            key: "X-Frame-Options",
            value: "ALLOWALL",
          },
          // Content Security Policy for iframe embedding
          {
            key: "Content-Security-Policy",
            value: "frame-ancestors 'self' https://colab.research.google.com https://*.googleusercontent.com https://*.google.com http://localhost:*",
          },
          // Allow cross-origin requests for development
          {
            key: "Access-Control-Allow-Origin",
            value: "*",
          },
          {
            key: "Access-Control-Allow-Methods",
            value: "GET, POST, PUT, DELETE, OPTIONS",
          },
          {
            key: "Access-Control-Allow-Headers",
            value: "Content-Type, Authorization",
          },
          // Allow microphone access in iframes
          {
            key: "Permissions-Policy",
            value: "microphone=*, camera=*, geolocation=*",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
