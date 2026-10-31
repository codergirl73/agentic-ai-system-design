import unittest
from agent import Session, add_artifact, build_context

class ContextTests(unittest.TestCase):
    def test_artifact_is_referenced(self):
        session = Session("Analyze sales")
        add_artifact(session, "table-1", "monthly totals", "artifact://table-1")
        self.assertIn("artifact://table-1", build_context(session))

    def test_context_obeys_word_budget(self):
        session = Session("summarize")
        session.events = ["one two three", "four five six"]
        context = build_context(session, token_budget=4)
        self.assertLessEqual(len(context.split()), 4)

    def test_invalid_budget_rejected(self):
        with self.assertRaises(ValueError):
            build_context(Session("goal"), 0)

if __name__ == "__main__":
    unittest.main()
