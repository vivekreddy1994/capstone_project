import unittest
from support_assistant.src.assistant import Assistant

class TestAssistant(unittest.TestCase):

    def setUp(self):
        self.assistant = Assistant()

    def test_handle_query(self):
        response = self.assistant.handle_query("What is the weather today?")
        self.assertIsInstance(response, str)
        self.assertNotEqual(response, "")

    def test_get_prompt(self):
        prompt = self.assistant.get_prompt("greeting")
        self.assertEqual(prompt, "Hello! How can I assist you today?")

    def test_process_request(self):
        result = self.assistant.process_request("Help me with my order.")
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()