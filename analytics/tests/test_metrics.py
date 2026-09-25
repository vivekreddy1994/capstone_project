import unittest
from analytics.src.metrics import calculate_metric_1, calculate_metric_2

class TestMetrics(unittest.TestCase):

    def test_calculate_metric_1(self):
        # Test case for calculate_metric_1 function
        input_data = [1, 2, 3, 4, 5]
        expected_output = 3.0  # Example expected output
        result = calculate_metric_1(input_data)
        self.assertEqual(result, expected_output)

    def test_calculate_metric_2(self):
        # Test case for calculate_metric_2 function
        input_data = [10, 20, 30]
        expected_output = 20.0  # Example expected output
        result = calculate_metric_2(input_data)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()