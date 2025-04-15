# Slash - Modern Frontend

A clean, modern frontend for the Slash price comparison app built with Next.js.

## Setup

### Requirements
- Node.js 18+
- Flask backend running on port 5000

### Quick Start
```bash
# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Features
- Product search with real-time loading indicators
- Wishlist management
- Toast notifications for user feedback
- Responsive design for all devices
- Integration with existing Flask backend

## Technology
- Next.js 14
- React 18
- Tailwind CSS
- ShadCN UI

## Structure
- `src/app` - Pages and routes
- `src/components` - Reusable UI components
- `src/components/ui` - Core UI components

## Backend Connection
The app connects to the Flask backend through API proxying configured in `next.config.js`. All requests to `/api/*`, authentication endpoints, and wishlist functions are automatically forwarded to the backend.

## Notes
- Make sure the Flask backend is running before starting the frontend
- The app uses API routes to avoid CORS issues with the backend 