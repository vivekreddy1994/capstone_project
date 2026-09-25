import unittest

from support_assistant.src.assistant import graph


class TestRagAcceptance(unittest.TestCase):
    def test_policy_route_retrieves_grounded_context(self):
        state = graph.invoke({"query": "What is the delivery fee?"})
        self.assertEqual(state["intent"], "policy_question")
        self.assertEqual(state["retrieved"][0]["id"], "doc_01")
        self.assertTrue(state["response"].answer.startswith("Based on the retrieved context:"))
        self.assertEqual(state["response"].confidence, 1.0)

    def test_general_route_has_no_sources(self):
        state = graph.invoke({"query": "What is the weather?"})
        self.assertEqual(state["intent"], "general_question")
        self.assertEqual(state["response"].sources, [])
        self.assertEqual(state["response"].confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
