"""
Application Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', ''),
    'database': os.getenv('DATABASE_NAME', 'car_database'),
    'type': os.getenv('DATABASE_TYPE', 'postgresql')
}

# API Configuration
API_CONFIG = {
    'endpoint': os.getenv('API_ENDPOINT', 'http://localhost:8000/api'),
    'key': os.getenv('API_KEY', ''),
    'timeout': int(os.getenv('API_TIMEOUT', 30))
}

# Application Settings
APP_CONFIG = {
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'cache_enabled': os.getenv('CACHE_ENABLED', 'false').lower() == 'true',
    'cache_duration': int(os.getenv('CACHE_DURATION', 3600)),
    'max_search_results': int(os.getenv('MAX_SEARCH_RESULTS', 100))
}

# UI Configuration
UI_CONFIG = {
    'window_width': int(os.getenv('WINDOW_WIDTH', 1200)),
    'window_height': int(os.getenv('WINDOW_HEIGHT', 800)),
    'theme': os.getenv('THEME', 'default')
}

# Image Configuration
IMAGE_CONFIG = {
    'max_width': 800,
    'max_height': 600,
    'supported_formats': ('jpg', 'jpeg', 'png', 'gif', 'bmp'),
    'default_image': 'assets/images/placeholder.png'
}
