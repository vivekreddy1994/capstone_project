import os

class Config:
    def __init__(self):
        self.raw_data_path = os.path.join('data', 'raw')
        self.processed_data_path = os.path.join('data', 'processed')
        self.model_path = os.path.join('data', 'models')
        self.log_file = 'pipeline.log'
        self.scraping_timeout = 10  # seconds
        self.max_retries = 3
        self.api_key = os.getenv('API_KEY')  # Example for sensitive data
        self.database_url = 'sqlite:///data/database.db'  # Example for database connection

    def display_config(self):
        print("Configuration Settings:")
        print(f"Raw Data Path: {self.raw_data_path}")
        print(f"Processed Data Path: {self.processed_data_path}")
        print(f"Model Path: {self.model_path}")
        print(f"Log File: {self.log_file}")
        print(f"Scraping Timeout: {self.scraping_timeout}")
        print(f"Max Retries: {self.max_retries}")
        print(f"API Key: {self.api_key}")
        print(f"Database URL: {self.database_url}")