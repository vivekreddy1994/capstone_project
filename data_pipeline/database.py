import sqlite3
from pathlib import Path


def create_database(db_name="books.db"):
    connection = sqlite3.connect(db_name)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            in_stock INTEGER NOT NULL CHECK (in_stock IN (0, 1)),
            category_id INTEGER NOT NULL REFERENCES categories(category_id)
        );
        """
    )
    connection.commit()
    connection.close()


def insert_books(db_name, books):
    create_database(db_name)
    connection = sqlite3.connect(db_name)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        for book in books:
            connection.execute("INSERT OR IGNORE INTO categories(category_name) VALUES (?)", (book["category"],))
            category_id = connection.execute(
                "SELECT category_id FROM categories WHERE category_name = ?", (book["category"],)
            ).fetchone()[0]
            connection.execute(
                """INSERT INTO books(title, price_gbp, price_inr, rating, in_stock, category_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (book["title"], book["price_gbp"], book["price_inr"], book["rating"], int(book["in_stock"]), category_id),
            )
        connection.commit()
    finally:
        connection.close()


def load_books_to_db(books, db_name="books.db"):
    insert_books(db_name, books)


def run_required_queries(db_name="books.db"):
    queries = {
        "select_where": "SELECT title, price_gbp FROM books WHERE price_gbp > 20",
        "order_limit": "SELECT title, price_gbp FROM books ORDER BY price_gbp DESC LIMIT 10",
        "distinct": "SELECT DISTINCT category_name FROM categories ORDER BY category_name",
        "between": "SELECT title, price_gbp FROM books WHERE price_gbp BETWEEN 10 AND 20",
        "join": """SELECT c.category_name, b.title, b.rating
                  FROM books b JOIN categories c ON b.category_id = c.category_id
                  ORDER BY b.rating DESC, c.category_name, b.title LIMIT 10""",
    }
    connection = sqlite3.connect(db_name)
    try:
        return {name: connection.execute(sql).fetchall() for name, sql in queries.items()}
    finally:
        connection.close()


def pandas_join_comparison(db_name="books.db"):
    import pandas as pd

    connection = sqlite3.connect(db_name)
    try:
        sql_join = """SELECT c.category_name, b.title, b.rating
                      FROM books b JOIN categories c ON b.category_id = c.category_id
                      ORDER BY b.rating DESC, c.category_name, b.title LIMIT 10"""
        sql_result = pd.read_sql(sql_join, connection)
        books = pd.read_sql("SELECT title, rating, category_id FROM books", connection)
        categories = pd.read_sql("SELECT category_id, category_name FROM categories", connection)
        merged = pd.merge(books, categories, on="category_id", how="inner")
        merged_result = merged.sort_values(["rating", "category_name", "title"], ascending=[False, True, True]).head(10)
        merged_result = merged_result[["category_name", "title", "rating"]].reset_index(drop=True)
        return sql_result.reset_index(drop=True), merged_result
    finally:
        connection.close()
