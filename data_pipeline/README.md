# Books Data Pipeline

## Run

```powershell
python -m pip install -r data_pipeline/requirements.txt
python -m data_pipeline.main
```

The extractor uses `requests` and `BeautifulSoup` against Books to Scrape, reads five catalogue pages (100 books), and follows each detail page to capture the category. The cleaner strips GBP symbols, parses `rating` from One-Five to integers 1-5, parses `in_stock` from availability text, and computes `price_inr = price_gbp * 105.50`. The fixed project rate is exactly **1 GBP = 105.50 INR**; no currency API is used. Unexpected numeric values are median-imputed and unknown categories are labeled `Unknown`.

## Database

`database.py` creates normalized SQLite tables:

- `categories(category_id PRIMARY KEY, category_name UNIQUE)`
- `books(book_id PRIMARY KEY, title, price_gbp, price_inr, rating, in_stock, category_id FOREIGN KEY)`

The pipeline validates the cleaned frame, inserts rows into `data_pipeline/books.db`, and writes `data_pipeline/query_outputs.txt`, `data_pipeline/join_sql_output.csv`, and `data_pipeline/join_pandas_output.csv`. `run_required_queries` executes five saved query forms covering `SELECT/WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, `BETWEEN`, and a categories/books `JOIN`. `pandas_join_comparison` loads the SQL join with `pd.read_sql`, reproduces it by merging the in-memory books and categories frames with `pd.merge`, and fails the run if the results differ.
