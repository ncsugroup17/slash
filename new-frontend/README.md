# Slash - New Frontend

This is the new frontend implementation for the Slash price comparison application using Next.js, React, and ShadCN UI.

## Technologies Used

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- ShadCN UI Components

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm or yarn

### Installation

1. Install dependencies using the provided scripts to avoid peer dependency issues:

```bash
# For Linux/Mac:
sh install.sh

# For Windows:
install.bat

# Or manually with:
npm install --legacy-peer-deps
```

2. Run the development server:

```bash
npm run dev
# or
yarn dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Features

- Modern UI with responsive design
- Dark mode support
- Integration with the existing Flask backend
- Search for products and compare prices
- User authentication (traditional and Google login)
- Wishlist functionality
- Product filtering and sorting

## Backend Integration

This frontend is designed to work with the existing Flask backend. It proxies all API requests to the backend server running on port 5000. This is configured in the `next.config.js` file.

Make sure your Flask backend is running at http://localhost:5000 before using this frontend.

### Handling Redirects

The application includes a custom API wrapper (`src/lib/api-wrapper.ts`) that ensures all redirects from the backend (port 5000) are properly handled to keep users on the frontend (port 3000). This prevents issues where users might be redirected to the backend server after logging in or performing other actions.

Client-side components for forms (login, register) have been implemented to properly handle these redirects.

## Project Structure

- `src/app`: Next.js app router pages
- `src/components`: Reusable React components
- `src/components/ui`: ShadCN UI components
- `src/lib`: Utility functions and API handlers

## Troubleshooting

If you encounter TypeScript errors related to props like `variant` or `size` in components, these are due to type definition issues but will not affect the functionality of the application since we've set `"strict": false` in the tsconfig.json.

If you experience redirect issues (being sent to port 5000 instead of staying on port 3000), make sure you're using the client-side components for forms and API interactions. 