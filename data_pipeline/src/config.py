# Configuration settings for the data pipeline

import os

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input and output file paths
INPUT_DATA_PATH = os.path.join(BASE_DIR, 'data', 'input_data.csv')
OUTPUT_DATA_PATH = os.path.join(BASE_DIR, 'data', 'output_data.csv')

# Environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Logging configuration
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

# Database configuration (if applicable)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')

# Other configuration settings can be added here as needed