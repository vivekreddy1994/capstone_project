import sys
from .data.pipeline import DataPipeline

def main():
    # Initialize the data pipeline
    pipeline = DataPipeline(
        source_url='http://books.toscrape.com/catalogue/page-1.html',
        db_name='processed_books.csv',
    )

    # Execute the data pipeline
    pipeline.run()

if __name__ == "__main__":
    main()