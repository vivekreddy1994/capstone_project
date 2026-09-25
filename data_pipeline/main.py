# File: /my-data-pipeline-project/my-data-pipeline-project/data_pipeline/main.py

import logging
from pathlib import Path
try:
    from .extractor import extract_books
    from .processor import process_books
    from .database import load_books_to_db, pandas_join_comparison, run_required_queries
    from .processor import clean_and_process_data, validate_data
    from .config import DATABASE_NAME
except ImportError:
    from extractor import extract_books
    from processor import process_books
    from database import load_books_to_db, pandas_join_comparison, run_required_queries
    from processor import clean_and_process_data, validate_data
    from config import DATABASE_NAME

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the data pipeline...")

    # Step 1: Extract book data
    logging.info("Extracting book data...")
    books = extract_books()
    
    # Step 2: Process the extracted data
    logging.info("Processing book data...")
    processed_frame = clean_and_process_data(books)
    validate_data(processed_frame)
    processed_books = processed_frame.to_dict(orient="records")
    
    # Step 3: Load the processed data into the database
    logging.info("Loading data into the database...")
    load_books_to_db(processed_books, DATABASE_NAME)
    results = run_required_queries(DATABASE_NAME)
    output_dir = Path(__file__).resolve().parent
    with open(output_dir / "query_outputs.txt", "w", encoding="utf-8") as output:
        for name, rows in results.items():
            output.write(f"{name}: {rows}\n")
    sql_result, merged_result = pandas_join_comparison(DATABASE_NAME)
    if not sql_result.equals(merged_result):
        raise RuntimeError("SQL JOIN and pandas merge results differ")
    sql_result.to_csv(output_dir / "join_sql_output.csv", index=False)
    merged_result.to_csv(output_dir / "join_pandas_output.csv", index=False)
    
    logging.info("Data pipeline completed successfully.")

if __name__ == "__main__":
    main()