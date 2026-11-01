# Module 3 — Document Processing, Chunking and Embeddings

**Level:** Beginner → Intermediate → Advanced  
**Estimated time:** 3–4 hours  
**Prerequisites:** Module 2 — RAG Fundamentals; basic Python  
**Build:** A document preparation pipeline that converts raw files into searchable, traceable chunks.

> **Learning sequence:** understand the problem → inspect examples → learn design choices → implement → test → evaluate → explain trade-offs.

## Learning outcomes

By the end, you should be able to:

- Explain the stages between a raw document and a searchable knowledge base.
- Describe parsing, normalization, metadata, chunking, and provenance.
- Compare fixed-size, sentence, paragraph, recursive, structure-aware, and semantic chunking.
- Calculate chunk counts and understand overlap.
- Explain embeddings, vector dimensions, similarity, and model selection.
- Generate embeddings using Python.
- Store vectors with text and metadata, and validate an index.
- Diagnose document-processing and embedding failures.
- Design a safe and observable ingestion pipeline.

## The big picture

A PDF, HTML page, Word file, or support ticket is not automatically ready for semantic search. A RAG system must turn source material into clean, meaningful, traceable units.

~~~mermaid
flowchart TD
    A["Source documents"] --> B["Load and identify file type"]
    B --> C["Extract text and structure"]
    C --> D["Clean and normalize"]
    D --> E["Split into meaningful chunks"]
    E --> F["Attach metadata and source locations"]
    F --> G["Generate embeddings"]
    G --> H["Store text, vectors and metadata"]
    H --> I["Validate the index"]
    I --> J["Search-ready knowledge base"]
    C --> X["Quarantine parsing failures"]
~~~

Think of the pipeline as a factory. The input is unstructured source material. The output is a collection of small, searchable records with enough information to explain where each record came from.

---

# Lesson 1 — Document ingestion and parsing

## 1.1 What is ingestion?

**Document ingestion** is the process of bringing source data into an application and preparing it for downstream processing.

Typical sources include PDF handbooks and research papers, DOCX reports, HTML knowledge-base articles, Markdown files, code documentation, CSV exports, tickets, and database records.

A production ingestion service should identify the source, validate the file, extract content, record errors, and preserve provenance.

## 1.2 Parsing: extracting text and structure

A parser converts a file format into content the application can process.

Consider a PDF page containing:

**Late Submission Policy**
- Assignments are due by 11:59 PM.
- Late work loses 10% per calendar day.
- Approved extensions use the revised deadline.

A good parser should preserve the heading and its relationship to the bullets, the order of statements, page number, document identity, and tables or lists where possible.

A poor parser might return the same words in the wrong order, omit table cells, or combine a footer with the main paragraph. The embedding model cannot recover structure that was lost during extraction.

## 1.3 Different formats need different parsing strategies

| Source | Typical extraction approach | Common difficulty |
|---|---|---|
| Text-based PDF | PDF text extraction | Multi-column reading order |
| Scanned PDF | OCR and possibly layout analysis | Recognition errors |
| DOCX | Paragraph, heading, and table extraction | Tables and nested structure |
| HTML | DOM parsing and boilerplate removal | Navigation and repeated page elements |
| Markdown | Parse headings, lists, and code fences | Preserve hierarchy and code blocks |
| CSV | Parse rows and columns | Headers and row meaning |

**OCR** means optical character recognition: software identifies text in an image or scanned page. OCR can introduce substitutions, so extracted content should be checked when accuracy matters.

## 1.4 Parsing quality checks

Before chunking, check:

1. Did extraction return non-empty text?
2. Is text length plausible for the source?
3. Are page numbers and headings preserved?
4. Are tables readable and in the right order?
5. Are there replacement characters or repeated symbols?
6. Did OCR confidence indicate uncertain regions?
7. Can the content be traced back to the original file?

Example document record:

~~~python
document = {
    "document_id": "handbook-2026",
    "source_uri": "policies/handbook.pdf",
    "file_type": "pdf",
    "version": "2026-08",
    "status": "parsed",
    "page_count": 24,
    "extracted_characters": 18420
}
~~~

This describes the document; it is not the document's full content.

## 1.5 Worked example: a parsing problem

Suppose a two-column PDF is extracted in this order:
- Left column heading: Refunds
- Right column heading: Shipping
- Left column paragraph: refund requests must be submitted...
- Right column paragraph: orders ship within...

If the parser interleaves the columns, a chunk may combine a refund rule with shipping information. Search can then retrieve a misleading passage.

**Design lesson:** parsing quality is part of retrieval quality. Inspect representative documents before choosing chunking or embedding strategies.

### Checkpoint

1. What is the difference between ingestion and parsing?
2. Why is OCR sometimes needed?
3. Give two examples of document structure that should be preserved.
4. What could go wrong if a parser interleaves two PDF columns?

---

# Lesson 2 — Cleaning, normalization, metadata and provenance

## 2.1 Cleaning is not deleting everything unusual

Cleaning removes extraction noise while preserving meaning.

Possible tasks:
- Remove repeated page headers and footers when they add no meaning.
- Normalize whitespace and line endings.
- Repair obvious line-break artifacts.
- Remove duplicated content caused by extraction.
- Preserve punctuation, mathematical notation, code, and meaningful symbols.
- Keep table labels associated with their values.

Do not aggressively strip punctuation or numbers. In technical documentation, C++, v1.2.3, foo.bar, and IP addresses may be important identifiers.

## 2.2 Normalization

Normalization makes equivalent content more consistent. Examples include standardizing line endings, applying consistent Unicode normalization, collapsing accidental whitespace, and standardizing metadata fields and date formats.

Avoid changing the original meaning. Keep an immutable original source or reliable source reference so transformations can be audited.

## 2.3 Metadata: information about the content

| Field | Example | Why it matters |
|---|---|---|
| document_id | handbook-2026 | Groups chunks from one document |
| chunk_id | handbook-2026-p2-c3 | Identifies one chunk |
| source_uri | policies/handbook.pdf | Links back to source |
| page | 2 | Supports citations |
| heading | Late submissions | Preserves topic context |
| version | 2026-08 | Supports freshness |
| access_scope | students | Helps enforce authorization |
| created_at | 2026-08-15 | Supports lifecycle management |

**Provenance** means knowing where content came from and how it was produced. A chunk should be traceable to its source document and location.

## 2.4 Example chunk record

~~~python
chunk = {
    "chunk_id": "handbook-2026-p2-c1",
    "document_id": "handbook-2026",
    "text": "Late submissions lose 10 percent per calendar day.",
    "source_uri": "policies/handbook.pdf",
    "page": 2,
    "heading": "Late submissions",
    "version": "2026-08",
    "access_scope": "students"
}
~~~

When retrieval returns this chunk, the application can cite the document and page, filter by version, and check whether the user may access it.

## 2.5 Security and privacy at ingestion

Treat documents as data, not as trusted instructions. A document can contain misleading text, malicious prompt-injection instructions, or sensitive information.

A robust ingestion system should:
- Accept files only from approved sources.
- Validate file type and size.
- Scan uploads according to organizational controls.
- Avoid executing macros, scripts, or embedded active content.
- Apply data classification and access labels.
- Avoid indexing secrets or unnecessary personal information.
- Preserve permissions so retrieval cannot expose restricted content.
- Log processing events without copying sensitive document text into logs.

Authorization must be enforced by the application and retrieval layer. A prompt telling the model not to reveal restricted data is not an access-control system.

### Checkpoint

Explain why document_id, page, version, and access_scope can all matter when returning an answer.

---

# Lesson 3 — Chunking: turning documents into useful units

## 3.1 What is a chunk?

A **chunk** is a smaller piece of a document that is stored and retrieved as a unit.

A long document may contain hundreds of unrelated topics. Retrieving the whole document for every question can add irrelevant information, consume context, make citations imprecise, and make ranking less focused.

Chunking aims to create passages small enough to retrieve precisely but large enough to preserve the information needed to answer a question.

## 3.2 Chunk size: the central trade-off

Imagine a 20-page employee handbook.

- Very large chunks may contain several policies. Retrieval returns lots of irrelevant text.
- Very small chunks may split a rule from its exception or remove needed context.
- A useful chunk often corresponds to a coherent paragraph, section, or group of related sentences.

There is no universal best chunk size. It depends on document structure, question types, embedding model limits, and evaluation results.

## 3.3 Common chunking strategies

### A. Fixed-size chunking

Split text every N tokens or characters.

Example with 100-token chunks:
- Chunk 1: tokens 1–100
- Chunk 2: tokens 101–200
- Chunk 3: tokens 201–300

**Advantages:** simple, predictable, easy to batch.  
**Limitations:** can cut sentences, tables, or ideas in half.

### B. Fixed-size chunking with overlap

Overlap repeats a small region at the boundary.

Example: chunk size 100 tokens, overlap 20 tokens:
- Chunk 1: 1–100
- Chunk 2: 81–180
- Chunk 3: 161–260

The overlap gives a boundary-spanning statement a chance to appear in either adjacent chunk.

**Trade-off:** overlap can improve continuity, but increases storage, embedding cost, and duplicate retrieval.

### C. Sentence-based chunking

Split on sentence boundaries, then group sentences until a target size is reached.

**Advantages:** less likely to split a sentence.  
**Limitations:** a sentence may be too long or lack context; sentence boundaries are not always easy to detect in PDFs and technical text.

### D. Paragraph-based chunking

Use paragraphs as natural units.

**Advantages:** preserves the author's grouping of ideas.  
**Limitations:** paragraph lengths vary; some are too short and others too long.

### E. Structure-aware chunking

Use document structure such as heading hierarchy, sections, HTML elements, Markdown headings, lists, table boundaries, and code blocks.

For example, include the heading "Late submissions" in each chunk from that section. This helps a passage remain understandable when retrieved independently.

### F. Semantic chunking

Use content similarity or topic changes to decide where one chunk ends and another begins.

**Advantages:** can preserve coherent topics even when paragraph boundaries are poor.  
**Limitations:** more complex, may require embeddings or extra processing, and still needs evaluation.

## 3.4 Strategy comparison

| Strategy | Preserves structure? | Complexity | Useful when |
|---|---|---|---|
| Fixed-size | Low | Low | Baseline and predictable text |
| Fixed-size + overlap | Some continuity | Low | Boundary context matters |
| Sentence-based | Sentence boundaries | Medium | Prose with clear sentences |
| Paragraph-based | Paragraphs | Low | Well-written narrative |
| Structure-aware | Headings, lists, tables | Medium | Manuals, policies, technical docs |
| Semantic | Topic continuity | Higher | Natural topic boundaries matter |

A practical starting point for manuals is structure-aware chunking with a maximum token size. For plain text without reliable structure, fixed-size or sentence grouping can provide a baseline.

## 3.5 Chunking diagram

~~~mermaid
flowchart TD
    D["Extracted document"] --> S["Detect headings and sections"]
    S --> P["Split into paragraphs or blocks"]
    P --> G["Group related blocks"]
    G --> L{"Within token limit?"}
    L -->|Yes| C["Create chunk"]
    L -->|No| F["Split large block carefully"]
    F --> C
    C --> M["Attach heading and source metadata"]
    M --> V["Validate chunk"]
~~~

## 3.6 Worked calculation: no overlap

A document has 1,000 tokens. Chunk size is 200 tokens. There is no overlap.

\[
N = \left\lceil \frac{1000}{200} \right\rceil = 5
\]

So the document produces **5 chunks**.

## 3.7 Worked calculation: with overlap

A document has 1,000 tokens. Chunk size is 200 tokens and overlap is 50 tokens.

Step size:

\[
S = 200 - 50 = 150
\]

Chunk start positions are 0, 150, 300, 450, 600, 750, and 900. The final chunk is shorter.

Therefore, **7 chunks** are required.

General formula for a non-empty document of length L, chunk size C, and overlap O, where 0 ≤ O < C:

\[
N =
\begin{cases}
1 & L \le C \\
1 + \left\lceil \frac{L-C}{C-O} \right\rceil & L > C
\end{cases}
\]

## 3.8 Python: simple chunking with overlap

This example uses character counts to make the mechanics visible. Real systems should generally measure token counts using the tokenizer appropriate to the embedding model.

~~~python
def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]
        if chunk:
            chunks.append({
                "start_char": start,
                "end_char": min(start + chunk_size, len(text)),
                "text": chunk
            })
        if start + chunk_size >= len(text):
            break

    return chunks

sample = (
    "A retrieval system searches a knowledge base. "
    "It returns passages that may help answer a question. "
    "The answer should be grounded in those passages. "
) * 8

chunks = chunk_text(sample, chunk_size=120, overlap=20)
for item in chunks:
    print(item["start_char"], item["end_char"], item["text"])
~~~

## 3.9 Chunking tests

~~~python
def test_no_empty_chunks():
    result = chunk_text("abcdefghij", chunk_size=4, overlap=1)
    assert all(item["text"] for item in result)

def test_reconstruct_coverage():
    source = "abcdefghijklmnopqrstuvwxyz"
    result = chunk_text(source, chunk_size=8, overlap=2)
    covered = set()
    for item in result:
        covered.update(range(item["start_char"], item["end_char"]))
    assert covered == set(range(len(source)))

def test_invalid_overlap():
    try:
        chunk_text("hello", chunk_size=5, overlap=5)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

test_no_empty_chunks()
test_reconstruct_coverage()
test_invalid_overlap()
print("Chunking tests passed")
~~~

## 3.10 Chunking mistakes to watch for

- Splitting a table row from its column headings.
- Separating a rule from its exception.
- Removing a heading that gives the passage its meaning.
- Creating chunks mostly made of boilerplate.
- Using overlap so large that the index contains many duplicates.
- Choosing chunk size by habit rather than evaluation.
- Measuring characters while assuming they are tokens.

### Checkpoint

For a policy manual containing headings, paragraphs, and tables, which chunking strategy would you start with? Explain how you would preserve table headers and section names.

---

# Lesson 4 — Embeddings: representing meaning as vectors

## 4.1 What is an embedding?

An **embedding** is a numerical representation of an input, such as text, produced by an embedding model.

For example, an embedding model may map:
- "How can I return an item?"
- "What is the product refund process?"

to vectors that are relatively close in the model's vector space because the sentences express related ideas.

A vector is an ordered list of numbers:

\[
v = [0.12, -0.08, 0.44, 0.91, \ldots]
\]

The values are learned representations. They are not usually human-readable labels, and an individual dimension generally does not correspond to a simple concept such as refund or shipping.

## 4.2 What does vector dimension mean?

The **dimension** is the number of numeric values in an embedding vector.

- A 3-dimensional vector has 3 values.
- A 384-dimensional vector has 384 values.
- A 768-dimensional vector has 768 values.
- A 1,536-dimensional vector has 1,536 values.

Dimension is part of the embedding model's output format. It does not mean the model understands that many separate topics, and a larger dimension does not automatically mean better retrieval.

Example:

\[
v_1 = [0.2, 0.7, -0.1, 0.4]
\]

This vector has dimension 4.

If a model returns 768 values for each text, every vector stored in that index must use a compatible embedding configuration. You cannot directly compare a 384-dimensional query vector with a 768-dimensional document vector.

## 4.3 How embeddings are used in RAG

At ingestion time:
1. Split a document into chunks.
2. Send each chunk to the embedding model.
3. Receive a vector for each chunk.
4. Store the vector with original text and metadata.

At query time:
1. Embed the user's question using a compatible query encoder.
2. Compare the query vector with stored chunk vectors.
3. Retrieve the nearest candidates.
4. Pass candidate text to the generation model.

~~~mermaid
flowchart TD
    D["Document chunk"] --> E["Embedding model"]
    E --> V["Document vector"]
    V --> DB[("Vector index")]
    Q["User question"] --> QE["Compatible query encoder"]
    QE --> QV["Query vector"]
    QV --> S["Similarity search"]
    DB --> S
    S --> R["Relevant text chunks"]
~~~

Some embedding models use different query and document encoding instructions or separate encoders. Follow the model's documented retrieval interface rather than assuming every model uses identical calls.

## 4.4 Similarity and cosine similarity

A vector index needs a way to compare vectors. Common choices include cosine similarity, dot product, and Euclidean distance (L2).

Cosine similarity compares the angle between two vectors:

\[
\operatorname{cosine}(A,B) =
\frac{A \cdot B}{\|A\|\|B\|}
\]

### Worked example

Let:

\[
A=(1,0), \quad B=(0.8,0.6)
\]

Dot product:

\[
A \cdot B = (1)(0.8)+(0)(0.6)=0.8
\]

Both vector lengths are 1:

\[
\|A\|=1, \quad \|B\|=\sqrt{0.8^2+0.6^2}=1
\]

Therefore:

\[
\operatorname{cosine}(A,B)=0.8
\]

This is a similarity score, not an 80% probability that the passage is correct. Similarity ranks candidates and must be validated against real questions.

## 4.5 Embedding model selection

| Criterion | Questions to ask |
|---|---|
| Retrieval quality | Does it retrieve passages that answer real user questions? |
| Language coverage | Does it support languages in the corpus and queries? |
| Domain performance | Does it handle legal, scientific, code, or business language? |
| Dimension | What vector size does it output? |
| Context limit | How much text can be embedded in one request? |
| Latency | How quickly can it embed queries and batches? |
| Cost | What do document indexing and query embedding cost? |
| Deployment | Hosted API, local model, hardware and data constraints? |
| License and governance | Are usage and data-handling terms acceptable? |

Do not choose an embedding model from a leaderboard alone. Evaluate it on your own corpus and representative questions.

## 4.6 Embedding consistency and index compatibility

A vector index should record the embedding configuration used to create its vectors:
- Model name and version.
- Vector dimension.
- Normalization behavior.
- Similarity metric.
- Query/document encoding instructions, if applicable.
- Index version and creation time.

If you change embedding models, you generally need to re-embed the corpus and rebuild or separately version the index. Mixing incompatible vectors produces invalid comparisons.

### Checkpoint

1. What does vector dimension represent?
2. Why must query and document vectors be compatible?
3. Why is a similarity score not a confidence percentage?
4. Name four criteria for selecting an embedding model.

---

# Lesson 5 — Hands-on embedding generation in Python

This lesson uses the sentence-transformers library with a small publicly available model. It is an educational local example. For production, review the model card, license, privacy requirements, runtime resources, and benchmark performance before adoption.

## 5.1 Install the package

~~~bash
python -m pip install sentence-transformers
~~~

## 5.2 Generate embeddings

~~~python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

passages = [
    "Late submissions lose 10 percent per calendar day.",
    "Approved extensions use the revised deadline.",
    "Orders usually ship within two business days.",
]

vectors = model.encode(
    passages,
    normalize_embeddings=True,
    convert_to_numpy=True
)

print("Number of passages:", len(passages))
print("Embedding matrix shape:", vectors.shape)
print("Dimension per vector:", vectors.shape[1])
~~~

The output shape is (number_of_passages, embedding_dimension). The exact dimension comes from the selected model; inspect it rather than hardcoding assumptions.

## 5.3 Embed a query and rank passages

~~~python
import numpy as np

query = "What happens if an assignment is submitted late?"
query_vector = model.encode(
    [query],
    normalize_embeddings=True,
    convert_to_numpy=True
)[0]

scores = vectors @ query_vector
ranked_indices = np.argsort(scores)[::-1]

for index in ranked_indices:
    print(f"{scores[index]:.3f} | {passages[index]}")
~~~

Because the example normalizes vectors, the dot product is equivalent to cosine similarity. The ranking is illustrative and depends on the model.

## 5.4 Keep vectors, text, and metadata together

~~~python
records = []

for index, text in enumerate(passages):
    records.append({
        "id": f"policy-{index + 1}",
        "text": text,
        "source": "sample-policy",
        "page": index + 1,
        "embedding": vectors[index].tolist()
    })

assert len(records) == len(passages)
assert all(len(record["embedding"]) == vectors.shape[1] for record in records)
~~~

A vector alone is not enough for a RAG system. The system needs original text for context and metadata for citations, filtering, and permissions.

## 5.5 Batch embedding for larger collections

For large corpora, embed in batches rather than sending every chunk as a separate request.

~~~python
def embed_in_batches(model, texts, batch_size=32):
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    output = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        batch_vectors = model.encode(
            batch,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        output.extend(batch_vectors)
    return output
~~~

Batch size affects memory use, throughput, and latency. Tune it for the hardware and model rather than assuming a single value is optimal.

## 5.6 Practical exercise

1. Add five more policy passages.
2. Write five questions, including paraphrases that do not reuse the passage's exact wording.
3. Generate embeddings for all passages.
4. Retrieve the top two passages per question.
5. Record whether the correct passage appears in the top two.
6. Inspect failures and explain whether they are caused by parsing, chunking, embedding, or ranking.

This tiny sample is a debugging exercise, not a benchmark. Meaningful model comparisons require a representative evaluation set.

---

# Lesson 6 — Vector storage and index lifecycle

## 6.1 What is a vector index?

A vector index stores vectors in a structure that supports similarity search. A vector database commonly adds persistence, metadata filtering, updates, replication, and operational features.

A conceptual record:

~~~python
{
    "id": "handbook-p2-c1",
    "vector": [0.12, -0.08, 0.44],
    "text": "Late submissions lose 10 percent...",
    "metadata": {
        "document_id": "handbook-2026",
        "page": 2,
        "version": "2026-08"
    }
}
~~~

The three essential pieces are vector for similarity search, text for generation context, and metadata for citations, filtering, permissions, and lifecycle management.

## 6.2 Approximate nearest-neighbor search

For a small dataset, comparing the query with every vector may be practical. For very large collections, systems often use **approximate nearest-neighbor (ANN)** indexes to reduce search time.

ANN methods trade some exactness for speed and scalability. Index choice depends on collection size, update patterns, latency targets, memory, and recall.

Module 4 explores retrieval algorithms and ranking in more depth.

## 6.3 Metadata filtering

Suppose a user asks about a policy. The index contains the current student handbook, archived student handbook, staff-only handbook, and public course guide.

The application should apply the user's permissions and relevant version constraints. A semantic match must not override authorization.

A robust sequence is:
1. Authenticate the user.
2. Determine the user's permitted document scope.
3. Apply authorization-aware filtering in the retrieval path.
4. Search only eligible content.
5. Recheck access before returning source links if permissions may have changed.

## 6.4 Index lifecycle

| Event | Expected action |
|---|---|
| New document | Parse, chunk, embed, index |
| Updated document | Reprocess changed content and retire old version safely |
| Deleted document | Remove or tombstone its indexed chunks |
| Embedding model change | Re-embed and build a compatible index |
| Parser bug fixed | Reprocess affected source documents |
| Permission change | Update access metadata and enforce new scope |

Use versioned indexes or controlled migrations so a partial rebuild does not leave users with a mixture of incompatible embeddings.

## 6.5 Idempotency

An ingestion operation is **idempotent** when retrying it does not create duplicate records or corrupt the index.

A common approach is stable IDs derived from document identity, version, and chunk location. Store processing status and content hashes so the system can detect unchanged inputs.

### Checkpoint

Explain what should happen when a document is updated, deleted, or reprocessed after a parser bug is fixed.

---

# Lesson 7 — Evaluation and troubleshooting

## 7.1 Evaluate each stage separately

A poor answer can originate at several stages. Measure each one independently.

| Stage | What to inspect | Example check |
|---|---|---|
| Parsing | Extraction fidelity | Are important sentences and tables preserved? |
| Cleaning | Content integrity | Were meaningful symbols or numbers removed? |
| Chunking | Context and boundaries | Does each chunk make sense by itself? |
| Embedding | Semantic representation | Do paraphrased relevant passages rank well? |
| Retrieval | Candidate quality | Is the expected passage in top K? |
| Generation | Evidence use | Does the answer stay within retrieved evidence? |

## 7.2 Chunking evaluation

Create representative questions and label which chunks contain supporting evidence.

Try different chunk sizes and overlap values. Compare Recall@K, Precision@K, duplicate result rate, context tokens per query, citation accuracy, and end-to-end answer quality.

A chunking configuration that improves recall but floods the prompt with duplicate passages may not improve the complete system.

## 7.3 Embedding evaluation

For each question, record relevant passages. Evaluate whether the embedding model ranks them near the top.

Compare candidate models on the same documents, chunking strategy, questions, relevance labels, and retrieval settings.

Change one variable at a time where possible. Otherwise it becomes difficult to explain why a result improved.

## 7.4 Troubleshooting table

| Symptom | Possible cause | Investigation |
|---|---|---|
| Search misses a relevant sentence | Parsing omitted it | Inspect extracted text |
| Chunk has half a table row | Chunk boundary ignored structure | Inspect table-aware parsing |
| Passage is hard to understand alone | Chunk too small or heading omitted | Add section context |
| Many near-duplicate results | Excessive overlap or repeated source text | Inspect chunk boundaries |
| Paraphrases retrieve poorly | Embedding model or query handling mismatch | Evaluate alternate model and queries |
| Query vectors have wrong shape | Model/config mismatch | Validate model version and dimension |
| Old policy appears | Version filtering failed | Inspect metadata and filters |
| User sees restricted content | Authorization not enforced | Audit retrieval permissions |
| Index contains duplicates | Ingestion is not idempotent | Check stable IDs and retry behavior |

## 7.5 Build an evaluation dataset

A small evaluation record:

~~~python
evaluation_case = {
    "question": "What is the late submission deduction?",
    "relevant_chunk_ids": ["handbook-2026-p2-c1"],
    "expected_source": "handbook-2026",
    "answerable": True
}
~~~

Also include unanswerable questions. A reliable system should not fabricate an answer simply because vaguely related chunks were retrieved.

---

# Lesson 8 — End-to-end implementation milestone

Build a small pipeline with these interfaces:

~~~python
def load_document(path):
    """Read an approved source and return extracted content + metadata."""
    raise NotImplementedError

def clean_document(document):
    """Normalize extraction noise without changing meaning."""
    raise NotImplementedError

def chunk_document(document, config):
    """Return text chunks with stable IDs and source locations."""
    raise NotImplementedError

def embed_chunks(chunks, model):
    """Return compatible vectors while preserving chunk metadata."""
    raise NotImplementedError

def validate_records(records, expected_dimension):
    """Check IDs, text, metadata, vector dimensions, and duplicates."""
    raise NotImplementedError
~~~

## Acceptance criteria

- [ ] A supported source document can be loaded.
- [ ] Parsing errors are reported, not silently ignored.
- [ ] Extracted text is cleaned without losing important content.
- [ ] Chunks preserve useful section context.
- [ ] Chunk IDs are stable and unique.
- [ ] Source metadata is retained.
- [ ] Every embedding has the expected dimension.
- [ ] Text, vectors, and metadata remain linked.
- [ ] Reprocessing does not create duplicate records.
- [ ] Tests cover empty files, malformed input, long paragraphs, tables, and invalid chunk settings.
- [ ] A sample query retrieves relevant chunks.
- [ ] Limitations and evaluation results are documented.

## Suggested project structure

~~~text
document-embedding-pipeline/
  data/
    sample/
  src/
    ingestion.py
    parsing.py
    cleaning.py
    chunking.py
    embeddings.py
    validation.py
  tests/
    test_parsing.py
    test_chunking.py
    test_embeddings.py
    test_validation.py
  README.md
  requirements.txt
~~~

---

# Lesson 9 — System design and interview preparation

## 9.1 Design prompt

**Design an ingestion pipeline for a company knowledge assistant.**

The company has:
- 100,000 documents.
- PDF, DOCX, HTML, and Markdown sources.
- Documents updated throughout the day.
- Different access permissions for employees and teams.
- A requirement to cite the exact source document and page or section.

### Clarifying questions

Before drawing architecture, ask:
1. How many new or changed documents arrive each day?
2. How quickly must updates become searchable?
3. What are the largest files and supported languages?
4. Are scanned PDFs common?
5. How are document permissions represented and updated?
6. What are the latency and availability targets?
7. Are documents allowed to leave the company's environment?

### Reference architecture

~~~mermaid
flowchart TD
    S["Approved sources"] --> Q["Ingestion queue"]
    Q --> V["Validate file and permissions"]
    V --> P["Parse and extract structure"]
    P --> C["Clean and chunk"]
    C --> M["Attach provenance and access metadata"]
    M --> E["Embedding workers"]
    E --> I["Versioned vector index"]
    I --> T["Index validation and publish"]
    P --> X["Quarantine and error report"]
~~~

### Design decisions to explain

- **Queue vs synchronous ingestion:** queues absorb bursts and isolate slow parsing jobs.
- **Batch vs streaming embeddings:** batches can improve throughput; streaming can reduce update delay.
- **Structure-aware vs fixed chunking:** choose based on source formats and retrieval evaluation.
- **Rebuild vs incremental updates:** incremental updates reduce work, but versioned rebuilds can simplify model migrations.
- **Centralized vs per-tenant indexes:** trade operational simplicity against isolation, access boundaries, and scale.
- **Retry and dead-letter handling:** retry transient failures; quarantine permanently malformed documents for review.
- **Observability:** measure documents processed, parse failure rate, chunk count, embedding latency, index lag, and duplicate rate.

### Failure scenarios

1. **Parser outage:** queue work, retry safely, and keep the last valid index available.
2. **Embedding provider unavailable:** pause or retry embedding jobs; do not publish a half-built index as complete.
3. **Document revoked:** remove or deny access to its chunks promptly.
4. **Embedding model upgraded:** build a new compatible index, evaluate it, then switch traffic deliberately.
5. **Malformed source:** quarantine it with an actionable error record.

## 9.2 Interview questions

### Beginner
1. What is document ingestion?
2. What is parsing?
3. Why do RAG systems split documents into chunks?
4. What is an embedding?
5. What does embedding dimension mean?

### Intermediate
6. Compare fixed-size and structure-aware chunking.
7. Why is overlap used, and what does it cost?
8. What is the difference between a document vector and a query vector?
9. Why must text and metadata be stored with embeddings?
10. How would you evaluate chunking quality?

### Advanced
11. How would you migrate a 100-million-vector index to a new embedding model?
12. How would you guarantee document deletion propagates to every derived chunk?
13. How would you enforce permissions when users belong to multiple teams?
14. How would you handle a document whose parser output changes after a library upgrade?
15. How would you reduce ingestion cost while meeting freshness targets?

### Strong answer structure

For any design question, structure your response as:
1. Requirements and assumptions.
2. Data sources and scale.
3. Architecture and data flow.
4. Storage and metadata model.
5. Failure handling and security.
6. Evaluation and observability.
7. Trade-offs and future improvements.

---

# Practice set — test your understanding

## A. Multiple-choice questions

**1. What is the main purpose of document parsing?**

A. Generate the final answer  
B. Extract content and structure from a source format  
C. Rank vector results  
D. Change embedding dimensions

**2. Which chunking method explicitly uses headings, sections, or document structure?**

A. Random splitting  
B. Structure-aware chunking  
C. Vector normalization  
D. Query expansion

**3. A chunk size is 200 tokens and overlap is 40 tokens. What is the step size?**

A. 40  
B. 160  
C. 200  
D. 240

**4. What does a 768-dimensional embedding contain?**

A. 768 documents  
B. 768 numeric values  
C. 768 words  
D. 768 topics with human-readable labels

**5. Why preserve source metadata with each chunk?**

A. To increase vector dimension  
B. To support citations, filtering, permissions, and provenance  
C. To make parsing unnecessary  
D. To guarantee every answer is correct

**6. What should happen if the embedding model changes to one with a different vector dimension?**

A. Mix old and new vectors in the same index without changes  
B. Rebuild or version a compatible index  
C. Truncate vectors randomly  
D. Change only the query prompt

**7. Which is a key risk of excessive chunk overlap?**

A. Fewer chunks  
B. Duplicate content and higher storage/embedding cost  
C. No metadata  
D. Lower source traceability

## B. Short-answer questions (2–3 marks)

1. Differentiate document ingestion and parsing.
2. Why should a parser preserve headings and table structure?
3. Define chunking and explain why it is needed in RAG.
4. Compare fixed-size and paragraph-based chunking.
5. What is chunk overlap? State one benefit and one drawback.
6. Define an embedding and vector dimension.
7. Why is a higher-dimensional embedding not automatically better?
8. Explain provenance and give two useful metadata fields.
9. Why must query and document embeddings be compatible?
10. What is idempotency in an ingestion pipeline?

## C. Calculation questions

**1. Chunk count without overlap**

A document contains 2,400 tokens. Chunk size is 400 tokens and overlap is zero. Calculate the number of chunks.

**2. Chunk count with overlap**

A document contains 1,000 tokens. Chunk size is 250 tokens and overlap is 50 tokens. Calculate the step size and number of chunks.

**3. Vector storage**

A collection contains 50,000 chunks. Each embedding has 768 dimensions. If each dimension is stored as a 4-byte float, estimate raw vector storage in bytes and MiB. Ignore metadata and index overhead.

**4. Batch count**

A pipeline must embed 10,000 chunks with a batch size of 128. How many batches are required if the last batch may be smaller?

**5. Cosine similarity**

Let A=(1,0) and B=(0,1). Calculate cosine similarity and explain what the result means geometrically.

## D. Applied design exercise

A research team wants to search 5,000 scientific papers, many of which contain two-column layouts, tables, equations, and references.

Design the document-processing pipeline. Include:
- Parsing choices for text PDFs and scanned PDFs.
- How you preserve headings, tables, equations, and page references.
- A chunking strategy and why you chose it.
- Metadata fields.
- Embedding model selection criteria.
- How you would evaluate retrieval quality.
- How you would reprocess documents after a parser upgrade.

---

# Answer key and worked solutions

## Multiple choice

1. **B** — parsing extracts text and structure from a source format.
2. **B** — structure-aware chunking uses document hierarchy.
3. **B** — step size = 200 − 40 = 160 tokens.
4. **B** — it contains 768 numeric values.
5. **B** — metadata supports traceability, filtering, authorization, and citations.
6. **B** — incompatible vectors require a compatible, separately versioned index or rebuild.
7. **B** — overlap can create duplicate content and increase cost.

## Short answers — key points

1. Ingestion is the overall process of bringing and preparing source data; parsing extracts content and structure from a particular format.
2. Headings and table structure preserve meaning and context when content is retrieved independently.
3. Chunking splits long documents into smaller retrievable passages, improving focused retrieval and context efficiency.
4. Fixed-size is predictable but may cut ideas; paragraph-based preserves natural units but paragraph lengths vary.
5. Overlap repeats boundary text to preserve continuity; it can increase duplicates, storage, and embedding cost.
6. An embedding is a numerical representation of input; dimension is the number of values in its vector.
7. Quality depends on model training, data, task, and evaluation, not dimension alone.
8. Provenance tracks origin and transformation; examples include source URI, document ID, page, and version.
9. Similarity search requires vectors in a compatible representation space and dimension.
10. Retrying the same ingestion job should not create duplicate or inconsistent records.

## Calculation solutions

**1.**

\[
2400 / 400 = 6
\]

So 6 chunks.

**2.**

Step size:

\[
250 - 50 = 200
\]

Chunk count:

\[
N=1+\left\lceil\frac{1000-250}{200}\right\rceil
=1+\lceil3.75\rceil=5
\]

So 5 chunks.

**3.**

Number of vector values:

\[
50,000 \times 768 = 38,400,000
\]

Raw storage:

\[
38,400,000 \times 4 = 153,600,000\text{ bytes}
\]

Using 1 MiB = 1,048,576 bytes:

\[
153,600,000 / 1,048,576 \approx 146.5\text{ MiB}
\]

This excludes IDs, metadata, text, database overhead, replicas, and ANN index structures.

**4.**

\[
\left\lceil\frac{10,000}{128}\right\rceil=79
\]

So 79 batches.

**5.**

\[
A\cdot B=(1)(0)+(0)(1)=0
\]

Both vector lengths are 1, so cosine similarity is 0. The vectors are perpendicular in this two-dimensional example.

---

# Completion checklist

- [ ] I can explain the path from raw file to searchable chunk.
- [ ] I can describe parsing and common extraction errors.
- [ ] I can explain why metadata and provenance matter.
- [ ] I can compare at least four chunking strategies.
- [ ] I can calculate chunk counts with overlap.
- [ ] I can explain embeddings and vector dimensions.
- [ ] I can generate embeddings in Python.
- [ ] I can explain vector similarity and compatibility.
- [ ] I can describe index updates, deletion, and re-embedding.
- [ ] I can evaluate parsing, chunking, and embedding separately.
- [ ] I can present an ingestion architecture and defend its trade-offs.

## Further reading and references

1. **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks** — Reimers and Gurevych (2019): https://arxiv.org/abs/1908.10084
2. **Text Embeddings by Weakly-Supervised Contrastive Pre-training** — Gao et al. (2021): https://arxiv.org/abs/2212.03533
3. **Sentence Transformers documentation:** https://www.sbert.net/
4. **Hugging Face model hub:** https://huggingface.co/models?pipeline_tag=sentence-similarity

When reading an embedding paper or model card, record: training objective, training data, intended task, vector dimension, supported languages, context length, evaluation benchmarks, license, and known limitations.

## What comes next?

**Module 4 — Information Retrieval:** move from preparing and embedding content to understanding how search systems retrieve and rank it, including inverted indexes, TF-IDF, BM25, vector search, and retrieval evaluation.
