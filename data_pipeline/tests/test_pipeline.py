import os
import sqlite3
import tempfile
import unittest

from data_pipeline.database import create_database, insert_books, run_required_queries
from data_pipeline.processor import clean_and_process_data, validate_data


class TestDataPipeline(unittest.TestCase):
    def setUp(self):
        self.database_path = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
        create_database(self.database_path)

    def tearDown(self):
        if os.path.exists(self.database_path):
            os.remove(self.database_path)

    def test_cleaning_and_fixed_conversion(self):
        raw = [{"title": "Book", "price": "£10.00", "star_rating": "Five", "availability": "In stock", "category": "Fiction"}]
        frame = clean_and_process_data(raw)
        self.assertEqual(frame.iloc[0]["price_gbp"], 10.0)
        self.assertEqual(frame.iloc[0]["price_inr"], 1055.0)
        self.assertEqual(frame.iloc[0]["rating"], 5)
        self.assertTrue(frame.iloc[0]["in_stock"])
        self.assertTrue(validate_data(frame))

    def test_normalized_schema_and_queries(self):
        books = [
            {"title": "A", "price_gbp": 10.0, "price_inr": 1055.0, "rating": 5, "in_stock": True, "category": "Fiction"},
            {"title": "B", "price_gbp": 25.0, "price_inr": 2637.5, "rating": 4, "in_stock": False, "category": "Travel"},
        ]
        insert_books(self.database_path, books)
        connection = sqlite3.connect(self.database_path)
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(tables, {"categories", "books"})
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM books").fetchone()[0], 2)
        connection.close()
        results = run_required_queries(self.database_path)
        self.assertEqual(len(results["order_limit"]), 2)
        self.assertEqual(results["distinct"], [("Fiction",), ("Travel",)])
        self.assertEqual(len(results["join"]), 2)


if __name__ == "__main__":
    unittest.main()
