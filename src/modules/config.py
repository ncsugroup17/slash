"""
Copyright (C) 2023 SE23-Team44
 
Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""
import os
class Config(object):
    DEBUG = False
    TESTING = False
    EMAIL_PASS = 'amkx fedi ilnm qahn'
    CLIENT_ID = 'REPLACE_WITH_CLIENT_ID'
    CLIENT_SECRET = 'REPLACE_WITH_CLIENT_SECRET'
    # SECRET_KEY = 'asdsdfsdfs13sdf_df%&'
    SECRET_KEY = os.getenv('SECRET_KEY', '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')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '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')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    GOOGLE_REDIRECT_URI = "http://localhost:5000/callback"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    Debug = True

class TestingConfig(Config):
    TESTING = True