import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION') or 'us-east-1'  
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    
    # Email Configuration
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER') or 'noreply@bytesizedtechnews.com'
    
     # Admin Configuration(redacted)
    
    
    
    # Google API Configuration(redacted)
    
    
    