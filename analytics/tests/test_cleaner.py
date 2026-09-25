import unittest
from src.data.cleaner import clean_data

class TestCleaner(unittest.TestCase):

    def test_clean_data(self):
        raw_data = {
            'name': ['Alice', 'Bob', None, 'David'],
            'age': [25, None, 30, 22],
            'email': ['alice@example.com', 'bob@example.com', 'invalid_email', 'david@example.com']
        }
        
        expected_cleaned_data = {
            'name': ['Alice', 'Bob', 'David'],
            'age': [25, 22],
            'email': ['alice@example.com', 'david@example.com']
        }
        
        cleaned_data = clean_data(raw_data)
        
        self.assertEqual(cleaned_data['name'], expected_cleaned_data['name'])
        self.assertEqual(cleaned_data['age'], expected_cleaned_data['age'])
        self.assertEqual(cleaned_data['email'], expected_cleaned_data['email'])

if __name__ == '__main__':
    unittest.main()