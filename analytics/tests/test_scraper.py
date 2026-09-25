import unittest
from src.data.scraper import Scraper  # Adjust the import based on your scraper implementation

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = Scraper()

    def test_scrape_data(self):
        # Assuming the scraper has a method called scrape_data
        data = self.scraper.scrape_data()
        self.assertIsInstance(data, list)  # Check if the data is a list
        self.assertGreater(len(data), 0)  # Check if the data is not empty

    def test_scrape_data_structure(self):
        data = self.scraper.scrape_data()
        # Assuming each item in the data is a dictionary with specific keys
        for item in data:
            self.assertIn('title', item)
            self.assertIn('price', item)
            self.assertIn('star_rating', item)
            self.assertIn('availability', item)

if __name__ == '__main__':
    unittest.main()