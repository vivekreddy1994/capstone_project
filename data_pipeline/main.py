# File: /my-data-pipeline-project/my-data-pipeline-project/data_pipeline/main.py

import logging
try:
    from .extractor import extract_books
    from .processor import process_books
    from .database import load_books_to_db
    from .config import DATABASE_NAME
except ImportError:
    from extractor import extract_books
    from processor import process_books
    from database import load_books_to_db
    from config import DATABASE_NAME

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the data pipeline...")

    # Step 1: Extract book data
    logging.info("Extracting book data...")
    books = extract_books()
    
    # Step 2: Process the extracted data
    logging.info("Processing book data...")
    processed_books = process_books(books)
    
    # Step 3: Load the processed data into the database
    logging.info("Loading data into the database...")
    load_books_to_db(processed_books, DATABASE_NAME)
    
    logging.info("Data pipeline completed successfully.")

if __name__ == "__main__":
    main()