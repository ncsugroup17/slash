/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Configure rewrites to proxy auth-related requests to the backend
  async rewrites() {
    return [
      // Handle Google OAuth endpoints
      {
        source: '/login/google',
        destination: 'http://localhost:5000/login/google',
      },
      {
        source: '/callback',
        destination: 'http://localhost:5000/callback',
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
      {
        source: '/logout',
        destination: 'http://localhost:5000/logout',
      },
      // Add wishlist endpoints
      {
        source: '/add-wishlist-item',
        destination: 'http://localhost:5000/add-wishlist-item',
      },
      {
        source: '/remove-wishlist-item',
        destination: 'http://localhost:5000/remove-wishlist-item',
      },
      {
        source: '/wishlist',
        destination: 'http://localhost:5000/wishlist',
      },
    ];
  },
  // Handle redirects for old frontend paths if needed
  async redirects() {
    return [
      {
        source: '/static/:path*',
        destination: 'http://localhost:5000/static/:path*',
        permanent: false,
      },
    ];
  },
  images: {
    domains: ['placehold.co', 'example.com'],
  },
};

module.exports = nextConfig; 