# Data Pipeline Project

This project is a data pipeline that scrapes book data from [books.toscrape.com](http://books.toscrape.com), processes the data, and loads it into a normalized SQLite database. The pipeline is designed to be modular, making it easy to maintain and extend.

## Installation Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd my-data-pipeline-project
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

## Execution Steps

1. **Run the data pipeline:**
   ```bash
   python data_pipeline/main.py
   ```

   This will initiate the scraping process, clean the data, and load it into the SQLite database.

2. **Access the SQLite database:**
   After execution, you can access the SQLite database to view the scraped data. The database file is located in the project directory.

## Design Decisions

- **Modular Structure:** The project is organized into separate modules for extraction, processing, and database interaction. This separation of concerns enhances maintainability and readability.
  
- **Data Normalization:** The database schema is designed to normalize the data, separating books and categories into distinct tables to reduce redundancy.

- **Error Handling:** The pipeline includes error handling mechanisms to manage potential issues during scraping and data processing.

- **Currency Conversion:** A fixed currency conversion rate is used for converting book prices from GBP to INR, ensuring consistency in the data.

- **Testing:** Unit tests are included to verify the functionality of each component, ensuring that the pipeline operates as expected.

## Future Improvements

- Implement a more sophisticated logging mechanism to track the scraping process and any errors encountered.
- Extend the pipeline to scrape additional data fields or from other sources.
- Optimize the data processing steps for larger datasets.