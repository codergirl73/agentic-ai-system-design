# Module 3 Project — Document Processing and Embedding Pipeline

A runnable Python project that turns Markdown and text files into traceable chunks, optionally generates embeddings, and runs semantic search. This is an educational baseline; PDF/OCR adapters and a persistent vector database are extension tasks.

## What it does

1. Reads .txt and .md files recursively.
2. Extracts Markdown heading context.
3. Normalizes whitespace while preserving punctuation.
4. Splits content into overlapping character windows.
5. Adds stable chunk IDs, source paths, headings, offsets, and content hashes.
6. Optionally generates Sentence Transformers embeddings.
7. Writes JSON Lines records and validates dimensions.
8. Searches embedded records using cosine similarity.

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell: `.venv\\Scripts\\Activate.ps1`

Core parsing and tests use only the standard library. Embeddings and search need optional packages.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Ingest without a model

```bash
python -m src.pipeline --input data/sample --output artifacts/chunks.jsonl
```

## Generate embeddings

```bash
python -m pip install sentence-transformers numpy
python -m src.pipeline --input data/sample --output artifacts/chunks_with_embeddings.jsonl --embed
```

The first model run may download `sentence-transformers/all-MiniLM-L6-v2` and requires internet access. You can change the model with `--model`.

```bash
python -m src.pipeline --input data/sample --output artifacts/chunks.jsonl --embed --chunk-size 900 --overlap 120
```

Chunk sizes are characters, not tokens. Production systems should use model-aware tokenization and evaluate chunking on labelled questions.

## Search

```bash
python -m src.pipeline --search "When is late work penalized?" --records artifacts/chunks_with_embeddings.jsonl
```

## Design notes and limitations

- IDs include the source content hash so changed source content creates new IDs.
- Metadata preserves source path, file type, heading, chunk index, and character offsets.
- The demo has no authorization layer; real systems must enforce document permissions during retrieval.
- Text is treated as untrusted source data, never as executable instructions.
- Add PDF parsing/OCR, table-aware parsing, token-based chunking, persistent vector storage, deletion propagation, retries, and a labelled evaluation set as next extensions.

## Curriculum

- [Module 3 guide](../../MODULE_3_DOCUMENT_PROCESSING.md)
- [Module 4 guide](../../MODULE_4_INFORMATION_RETRIEVAL.md)
