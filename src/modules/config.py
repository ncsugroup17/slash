"""
Copyright (C) 2023 SE23-Team44

Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""

import os


class Config(object):
    DEBUG = False
    TESTING = False
    EMAIL_PASS = 'siyq mvum iyle clqk'
    CLIENT_ID = 'REPLACE_WITH_CLIENT_ID'
    CLIENT_SECRET = 'REPLACE_WITH_CLIENT_SECRET'
    SECRET_KEY = os.getenv('SECRET_KEY', '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')
    GOOGLE_CLIENT_ID = os.getenv(
        'GOOGLE_CLIENT_ID',
        '92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com'
    )
    GOOGLE_CLIENT_SECRET = os.getenv(
        'GOOGLE_CLIENT_SECRET',
        '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'
    )
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    # Use environment variables for the callback URL or fall back to the default Flask callback
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', '')
    FRONTEND_URL = os.getenv('FRONTEND_URL', '')
    
    # Groq API Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama3-70b-8192')
    
    # AI Recommendation System Config
    AI_RECOMMENDATION_ENABLED = os.getenv('AI_RECOMMENDATION_ENABLED', 'True').lower() in ('true', 'yes', '1')
    AI_MAX_QUESTIONS = int(os.getenv('AI_MAX_QUESTIONS', '5'))
    AI_DEFAULT_TEMPERATURE = float(os.getenv('AI_DEFAULT_TEMPERATURE', '0.7'))
    
    @classmethod
    def is_ai_enabled(cls):
        """Check if AI recommendations are enabled"""
        return cls.AI_RECOMMENDATION_ENABLED and cls.GROQ_API_KEY


    @classmethod
    def get_google_redirect_uri(cls, request=None):
        """Dynamically determine the redirect URI based on the environment or request"""
        if cls.GOOGLE_REDIRECT_URI:
            return cls.GOOGLE_REDIRECT_URI
            
        # Fall back to using the current host with the callback path
        if request:
            host_url = request.host_url.rstrip('/')
            return f"{host_url}/callback"
            
        # Last resort fallback
        return "http://localhost:5000/callback"
        
    @classmethod
    def get_frontend_url(cls, request=None, default_to_backend=False):
        """Dynamically determine the frontend URL based on various sources"""
        # First check environment variable
        if cls.FRONTEND_URL:
            return cls.FRONTEND_URL
            
        # Try to get from request referrer or origin 
        if request:
            referrer = request.referrer or ''
            origin = request.headers.get('Origin', '')
            
            # Check for common frontend ports/domains
            for url in [referrer, origin]:
                if 'localhost:3000' in url or 'frontend' in url:
                    parts = url.split('/')
                    if len(parts) >= 3:
                        return f"{parts[0]}//{parts[2]}"
            
            # If default_to_backend is True, use the request's host_url
            if default_to_backend:
                return request.host_url.rstrip('/')
                
        # Last resort fallback - whoever called made this decision
        return "http://localhost:3000" if not default_to_backend else "http://localhost:5000"


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
