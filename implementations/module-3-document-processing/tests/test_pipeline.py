import tempfile
import unittest
from pathlib import Path

from src.pipeline import (
    chunk_document, load_documents, normalize_text,
    read_jsonl, validate_records, write_jsonl,
)


class NormalizeTextTests(unittest.TestCase):
    def test_normalizes_line_endings_and_whitespace(self):
        self.assertEqual(
            normalize_text("  A   title  \r\n\r\n\r\n B\tC "),
            "A title\n\nB C",
        )

    def test_preserves_meaningful_punctuation(self):
        self.assertEqual(normalize_text("C++ and v1.2.3"), "C++ and v1.2.3")


class ChunkingTests(unittest.TestCase):
    def setUp(self):
        self.document = {
            "document_id": "policy",
            "source_path": "policy.md",
            "file_type": "md",
            "text": "# Refunds\n\nRefund requests are accepted within 30 days. "
                    "Keep the receipt for verification.",
            "content_sha256": "abc123",
        }

    def test_heading_is_attached_to_chunks(self):
        chunks = chunk_document(self.document, chunk_size=200, overlap=20)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["metadata"]["heading"], "Refunds")

    def test_long_block_is_split_with_overlap(self):
        doc = dict(self.document)
        doc["text"] = "# Notes\n\n" + ("abcdefghij " * 20)
        chunks = chunk_document(doc, chunk_size=50, overlap=10)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(item["text"]) <= 50 for item in chunks))
        self.assertEqual(len({item["chunk_id"] for item in chunks}), len(chunks))

    def test_invalid_chunk_settings(self):
        with self.assertRaises(ValueError):
            chunk_document(self.document, chunk_size=10, overlap=10)
        with self.assertRaises(ValueError):
            chunk_document(self.document, chunk_size=0, overlap=0)


class FileAndValidationTests(unittest.TestCase):
    def test_load_and_round_trip_jsonl(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "input"
            root.mkdir()
            (root / "guide.md").write_text(
                "# Getting started\n\nRead the guide carefully.",
                encoding="utf-8",
            )
            docs = load_documents(root)
            records = chunk_document(docs[0], chunk_size=100, overlap=10)
            output = Path(temp) / "out" / "records.jsonl"
            write_jsonl(records, output)
            restored = read_jsonl(output)
            self.assertEqual(restored[0]["text"], records[0]["text"])
            self.assertEqual(restored[0]["metadata"]["source_path"], "guide.md")

    def test_duplicate_ids_are_rejected(self):
        record = {
            "chunk_id": "same", "document_id": "doc", "text": "valid",
            "metadata": {}, "embedding": None, "embedding_dimension": None,
        }
        with self.assertRaises(ValueError):
            validate_records([record, dict(record)])

    def test_wrong_embedding_dimension_is_rejected(self):
        record = {
            "chunk_id": "one", "document_id": "doc", "text": "valid",
            "metadata": {}, "embedding": [0.1, 0.2], "embedding_dimension": 2,
        }
        with self.assertRaises(ValueError):
            validate_records([record], expected_dimension=3)

    def test_malformed_jsonl_reports_line(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.jsonl"
            path.write_text('{"ok": true}\nnot-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2"):
                read_jsonl(path)


if __name__ == "__main__":
    unittest.main()
