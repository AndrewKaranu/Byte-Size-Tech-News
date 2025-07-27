import os
import json

# Load configuration from config.json
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print(f"Warning: config.json not found at {config_path}")
        return {}

# Load the JSON config
json_config = load_config()

# Database Configuration Logic
def get_database_url():
    # Check if we should use MySQL
    use_mysql = os.environ.get('USE_MYSQL', '').lower() in ('true', '1', 'yes') or json_config.get('USE_MYSQL', False)
    
    if not use_mysql:
        # Force SQLite for development
        return 'sqlite:///app.db'
    
    # Get individual components for MySQL
    db_host = os.environ.get('DB_HOST') or json_config.get('DB_HOST')
    db_port = os.environ.get('DB_PORT') or json_config.get('DB_PORT') or '3306'
    db_name = os.environ.get('DB_NAME') or json_config.get('DB_NAME')
    db_username = os.environ.get('DB_USERNAME') or json_config.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD') or json_config.get('DB_PASSWORD')
    
    # Check if we have valid individual components (not placeholders)
    if (all([db_host, db_name, db_username, db_password]) and 
        not any(placeholder in str(db_host) for placeholder in ['your-rds-endpoint', 'localhost', 'placeholder'])):
        # Build MySQL URL from individual components
        return f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # Fall back to full DATABASE_URL or SQLite
        full_database_url = os.environ.get('DATABASE_URL') or json_config.get('DATABASE_URL')
        if not full_database_url or 'your-rds-endpoint' in full_database_url:
            # Fallback to SQLite for development
            return 'sqlite:///app.db'
        else:
            return full_database_url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or json_config.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Database Configuration
    DATABASE_URL = get_database_url()
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 60,
            'charset': 'utf8mb4'
        }
    }
    
    # Email Configuration (Gmail SMTP)
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER') or json_config.get('EMAIL_SENDER') or 'bytesizedtechnews@gmail.com'
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') or json_config.get('EMAIL_PASSWORD') or 'your-app-password'
    
    # Admin Configuration
    ADMIN_KEY = os.environ.get('ADMIN_KEY') or json_config.get('ADMIN_KEY') or 'hey'    
    
    # Google API Configuration
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or json_config.get('GOOGLE_API_KEY')
    
    