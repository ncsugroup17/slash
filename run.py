"""
Run script with environment setup for the Flask application.
This allows running the app without hardcoded URLs.
"""
import os
import sys
import argparse
from src.modules.app import app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the application on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the application on')
    parser.add_argument('--frontend-url', help='URL of the frontend application')
    parser.add_argument('--redirect-uri', help='Google OAuth redirect URI')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Set environment variables if provided
    if args.frontend_url:
        os.environ['FRONTEND_URL'] = args.frontend_url
        
    if args.redirect_uri:
        os.environ['GOOGLE_REDIRECT_URI'] = args.redirect_uri
    
    # Print startup information
    print(f"Starting Flask application on {args.host}:{args.port}")
    if 'FRONTEND_URL' in os.environ:
        print(f"Frontend URL: {os.environ['FRONTEND_URL']}")
    if 'GOOGLE_REDIRECT_URI' in os.environ:
        print(f"Google redirect URI: {os.environ['GOOGLE_REDIRECT_URI']}")
    
    # Run the application
    app.run(host=args.host, port=args.port, debug=args.debug) 