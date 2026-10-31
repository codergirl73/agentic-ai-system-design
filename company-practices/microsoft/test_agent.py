import unittest
from agent import Document, retrieve_for_user

class AccessTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            Document("public", "quarterly revenue overview", frozenset({"alice", "bob"})),
            Document("private", "acquisition planning details", frozenset({"alice"})),
        ]

    def test_user_sees_only_authorized_matches(self):
        visible, _ = retrieve_for_user("bob", "acquisition planning", self.docs)
        self.assertEqual(visible, [])

    def test_authorized_user_can_retrieve(self):
        visible, _ = retrieve_for_user("alice", "acquisition planning", self.docs)
        self.assertEqual([d.doc_id for d in visible], ["private"])

    def test_audit_records_denied_documents(self):
        _, audit = retrieve_for_user("bob", "revenue", self.docs)
        denied = [entry for entry in audit if not entry["allowed"]]
        self.assertEqual(len(denied), 1)

if __name__ == "__main__":
    unittest.main()
