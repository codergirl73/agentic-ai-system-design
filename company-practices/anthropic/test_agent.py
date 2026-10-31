import unittest
from agent import Finding, run_research, conflicting_claims

class ResearchTests(unittest.TestCase):
    def researcher(self, question):
        return Finding(question, "evidence for " + question, "https://example.org/source")

    def test_returns_all_subquestions(self):
        result = run_research(["scope", "limits"], self.researcher, max_workers=2)
        self.assertEqual([x.question for x in result], ["limits", "scope"])

    def test_requires_source_url(self):
        with self.assertRaises(ValueError):
            run_research(["q"], lambda q: Finding(q, "claim", "file://local"), 1)

    def test_detects_disagreement(self):
        items = [Finding("q", "yes", "https://a.org"), Finding("q", "no", "https://b.org")]
        self.assertEqual(conflicting_claims(items), {"q": ["no", "yes"]})

if __name__ == "__main__":
    unittest.main()
