import unittest
from data_pipeline.extractor import extract_books
from data_pipeline.processor import clean_data
from data_pipeline.database import create_database, insert_books
import os

class TestDataPipeline(unittest.TestCase):

    def setUp(self):
        # Create a temporary SQLite database for testing
        self.db_path = 'test_books.db'
        create_database(self.db_path)

    def tearDown(self):
        # Remove the temporary database after tests
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_extract_books(self):
        books = extract_books()
        self.assertIsInstance(books, list)
        self.assertGreater(len(books), 0)
        self.assertIn('title', books[0])
        self.assertIn('price', books[0])
        self.assertIn('star_rating', books[0])
        self.assertIn('availability', books[0])
        self.assertIn('category', books[0])

    def test_clean_data(self):
        raw_data = [
            {'title': 'Book 1', 'price': '£10.00', 'star_rating': 'Five', 'availability': 'In stock', 'category': 'Fiction'},
            {'title': 'Book 2', 'price': '£15.00', 'star_rating': 'Four', 'availability': 'Out of stock', 'category': 'Non-Fiction'},
        ]
        cleaned_data = clean_data(raw_data)
        self.assertIsInstance(cleaned_data, list)
        self.assertEqual(len(cleaned_data), 2)
        self.assertEqual(cleaned_data[0]['price'], 1055.0)  # Assuming conversion rate is applied

    def test_insert_books(self):
        books = [
            {'title': 'Book 1', 'price': 1050.0, 'star_rating': 'Five', 'availability': 'In stock', 'category': 'Fiction'},
            {'title': 'Book 2', 'price': 1575.0, 'star_rating': 'Four', 'availability': 'Out of stock', 'category': 'Non-Fiction'},
        ]
        insert_books(self.db_path, books)
        # Verify that the books were inserted correctly
        # This part would typically involve querying the database and checking the results

if __name__ == '__main__':
    unittest.main()