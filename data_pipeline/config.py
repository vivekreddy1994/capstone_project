# Contents of /my-data-pipeline-project/my-data-pipeline-project/data_pipeline/config.py

CURRENCY_CONVERSION_RATE = 105.50
DATABASE_NAME = 'books.db'
BASE_URL = 'http://books.toscrape.com'
BOOKS_PER_PAGE = 20
MAX_PAGES = 5  # Adjust this to scrape more pages if needed
TIMEOUT = 10  # Timeout for requests in seconds
LOG_FILE = 'data_pipeline.log'