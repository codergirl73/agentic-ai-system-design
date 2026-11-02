"""Small document ingestion, chunking, embedding, and search pipeline.

Core parsing/chunking uses the Python standard library. Embeddings and semantic
search require the optional sentence-transformers and numpy packages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

SUPPORTED_SUFFIXES = {".txt", ".md"}


def normalize_text(text: str) -> str:
    """Normalize line endings and excess whitespace without stripping meaning."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def read_document(path: Path, root: Path) -> dict[str, Any]:
    """Read a supported UTF-8 document and preserve its source identity."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {suffix or '(no extension)'}")
    normalized = normalize_text(path.read_text(encoding="utf-8"))
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return {
        "document_id": Path(relative).with_suffix("").as_posix().replace("/", "-"),
        "source_path": relative,
        "file_type": suffix.lstrip("."),
        "text": normalized,
        "content_sha256": digest,
    }


def extract_markdown_blocks(text: str) -> list[tuple[str, str, int, int]]:
    """Return (heading, block_text, start, end) for paragraphs and text blocks."""
    blocks: list[tuple[str, str, int, int]] = []
    heading = ""
    offset = 0
    current_lines: list[str] = []
    current_start: int | None = None

    def flush(end_offset: int) -> None:
        nonlocal current_lines, current_start
        value = "\n".join(current_lines).strip()
        if value and current_start is not None:
            blocks.append((heading, value, current_start, end_offset))
        current_lines = []
        current_start = None

    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        line_start = offset
        line_end = offset + len(line)
        if stripped.startswith("#"):
            flush(line_start)
            heading = re.sub(r"^#+\s*", "", stripped).strip()
        elif not stripped:
            flush(line_start)
        else:
            if current_start is None:
                current_start = line_start
            current_lines.append(stripped)
        offset = line_end
    flush(offset)
    return blocks


def chunk_document(
    document: dict[str, Any],
    chunk_size: int = 900,
    overlap: int = 120,
) -> list[dict[str, Any]]:
    """Chunk document blocks into bounded character windows with overlap."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    records: list[dict[str, Any]] = []
    step = chunk_size - overlap
    for heading, block, block_start, _block_end in extract_markdown_blocks(document["text"]):
        for local_start in range(0, len(block), step):
            piece = block[local_start:local_start + chunk_size].strip()
            if not piece:
                continue
            chunk_index = len(records)
            stable_material = (
                f'{document["source_path"]}|{document["content_sha256"]}|'
                f"{chunk_index}|{local_start}"
            )
            chunk_id = hashlib.sha256(stable_material.encode("utf-8")).hexdigest()[:16]
            records.append({
                "chunk_id": chunk_id,
                "document_id": document["document_id"],
                "text": piece,
                "metadata": {
                    "source_path": document["source_path"],
                    "file_type": document["file_type"],
                    "heading": heading,
                    "chunk_index": chunk_index,
                    "start_char": block_start + local_start,
                    "end_char": block_start + local_start + len(piece),
                    "content_sha256": document["content_sha256"],
                },
                "embedding": None,
                "embedding_dimension": None,
            })
            if local_start + chunk_size >= len(block):
                break
    return records


def load_documents(input_dir: Path) -> list[dict[str, Any]]:
    """Load supported files recursively in deterministic path order."""
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    documents = []
    for path in sorted(input_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            documents.append(read_document(path, input_dir))
    return documents


def generate_embeddings(
    records: list[dict[str, Any]],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch_size: int = 32,
) -> list[dict[str, Any]]:
    """Attach normalized sentence embeddings to records."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if not records:
        return records
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Embedding dependencies missing. Install sentence-transformers and numpy."
        ) from exc

    model = SentenceTransformer(model_name)
    vectors = model.encode(
        [record["text"] for record in records],
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    for record, vector in zip(records, vectors):
        record["embedding"] = vector.astype(float).tolist()
        record["embedding_dimension"] = int(len(vector))
    return records


def validate_records(
    records: Iterable[dict[str, Any]],
    expected_dimension: int | None = None,
) -> None:
    """Raise ValueError when records are malformed or vector dimensions differ."""
    seen: set[str] = set()
    for record in records:
        required = {"chunk_id", "document_id", "text", "metadata", "embedding"}
        missing = required - record.keys()
        if missing:
            raise ValueError(f"Record missing fields: {sorted(missing)}")
        chunk_id = record["chunk_id"]
        if not chunk_id or chunk_id in seen:
            raise ValueError(f"Missing or duplicate chunk_id: {chunk_id}")
        seen.add(chunk_id)
        if not record["text"].strip():
            raise ValueError(f"Empty chunk: {chunk_id}")
        if not isinstance(record["metadata"], dict):
            raise ValueError(f"Metadata must be an object: {chunk_id}")
        vector = record["embedding"]
        if vector is not None:
            dimension = len(vector)
            if dimension == 0:
                raise ValueError(f"Empty embedding: {chunk_id}")
            if expected_dimension is not None and dimension != expected_dimension:
                raise ValueError(f"Expected dimension {expected_dimension}, got {dimension}")
            if record.get("embedding_dimension") != dimension:
                raise ValueError(f"Embedding dimension metadata mismatch: {chunk_id}")


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    """Write one JSON record per line, creating parent directories as needed."""
    validate_records(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON on line {line_number}") from exc
    validate_records(records)
    return records


def semantic_search(
    query: str,
    records: list[dict[str, Any]],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
) -> list[tuple[float, dict[str, Any]]]:
    """Return top-k (cosine score, record) pairs using normalized vectors."""
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if not query.strip():
        raise ValueError("query must not be empty")
    if not records or any(record["embedding"] is None for record in records):
        raise ValueError("All records must contain embeddings before searching")
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Search dependencies missing. Install sentence-transformers and numpy."
        ) from exc

    dimensions = {len(record["embedding"]) for record in records}
    if len(dimensions) != 1:
        raise ValueError("Records contain incompatible embedding dimensions")
    model = SentenceTransformer(model_name)
    query_vector = model.encode(
        [query], normalize_embeddings=True, convert_to_numpy=True
    )[0]
    if len(query_vector) not in dimensions:
        raise ValueError("Query and document embedding dimensions do not match")
    matrix = np.asarray([record["embedding"] for record in records], dtype=float)
    scores = matrix @ query_vector
    ranked = np.argsort(scores)[::-1][:top_k]
    return [(float(scores[index]), records[int(index)]) for index in ranked]


def main() -> None:
    parser = argparse.ArgumentParser(description="Module 3 document pipeline")
    parser.add_argument("--input", type=Path, help="Directory containing .txt/.md files")
    parser.add_argument("--output", type=Path, help="Output JSONL path")
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--overlap", type=int, default=120)
    parser.add_argument("--embed", action="store_true")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--search", help="Query an existing embedded JSONL file")
    parser.add_argument("--records", type=Path, help="JSONL file used with --search")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    if args.search:
        if not args.records:
            parser.error("--records is required with --search")
        results = semantic_search(
            args.search, read_jsonl(args.records), args.model, args.top_k
        )
        for score, record in results:
            print(f"\nscore={score:.4f} | {record['metadata']['source_path']}")
            print(f"heading={record['metadata']['heading']}")
            print(record["text"])
        return

    if not args.input or not args.output:
        parser.error("--input and --output are required for ingestion")
    all_records: list[dict[str, Any]] = []
    for document in load_documents(args.input):
        all_records.extend(
            chunk_document(document, chunk_size=args.chunk_size, overlap=args.overlap)
        )
    if args.embed:
        all_records = generate_embeddings(
            all_records, model_name=args.model, batch_size=args.batch_size
        )
    validate_records(all_records)
    write_jsonl(all_records, args.output)
    print(f"Processed {len(all_records)} chunks from {args.input}")
    print(f"Wrote records to {args.output}")


if __name__ == "__main__":
    main()
