# Module-Wise Interview Question Bank

This question bank grows alongside the curriculum. Questions are grouped by module and difficulty. They are original practice questions based on the subject matter, not claims about exact questions asked by specific companies.

**Answer standard:** Explain the concept, draw or describe the architecture where relevant, give an example, discuss limitations, and identify trade-offs.

## Module 1 — Foundations of Agentic AI

### Beginner
1. What is an AI agent? How is it different from an LLM?
2. What is the difference between a chatbot and an agent?
3. What are tools, memory, and planning in an agent?
4. Describe the observe–reason–act–evaluate loop.

### Intermediate
5. How should an agent decide whether to call a tool or answer directly?
6. What stopping conditions should an agent have?
7. How would you handle a tool timeout or malformed tool response?
8. When is a deterministic workflow preferable to an autonomous agent?

### Advanced system design
9. Design a research agent that searches papers, compares findings, and produces a cited report.
10. Design a bounded tool-execution loop with retries, timeouts, and a maximum action budget.
11. How would you measure task success, tool-use accuracy, and reliability?

## Module 2 — RAG Fundamentals

### Beginner
1. What is Retrieval-Augmented Generation, and why is it useful?
2. Explain the stages of a basic RAG pipeline.
3. How does RAG differ from fine-tuning?
4. Why should a RAG answer include source references?

### Intermediate
5. What happens when retrieval returns irrelevant or incomplete context?
6. How would you choose the number of chunks to pass to the generator?
7. What is the difference between retrieval quality and answer quality?
8. How can RAG reduce unsupported answers, and why does it not eliminate them?

### Advanced system design
9. Design a document question-answering system for an organization.
10. Design a RAG system that supports document updates and deletion.
11. How would you evaluate retrieval, groundedness, citation correctness, latency, and cost?

## Module 3 — Document Processing and Embeddings

### Beginner
1. What is an embedding?
2. Why do RAG systems split documents into chunks?
3. What are chunk size and chunk overlap?
4. What metadata might you store with each chunk?

### Intermediate
5. Compare fixed-size, recursive, and semantic chunking.
6. How can tables, code, and long PDFs complicate document ingestion?
7. What is cosine similarity, and what does it measure?
8. How would you re-index documents when the embedding model changes?

### Advanced system design
9. Design a scalable ingestion pipeline for millions of mixed-format documents.
10. Design an incremental indexing system that handles updates and deletions.
11. How would you monitor ingestion failures, embedding drift, and index freshness?

## Module 4 — Information Retrieval

### Beginner
1. Explain lexical search and semantic search.
2. What is an inverted index?
3. What is BM25?
4. What is vector similarity search?

### Intermediate
5. Compare sparse retrieval and dense retrieval.
6. Why can keyword search outperform vector search for some queries?
7. Explain Precision@K and Recall@K.
8. What do MRR and NDCG measure?

### Advanced system design
9. Design a search service that combines keyword and vector retrieval.
10. How would you build a representative retrieval evaluation dataset?
11. How would you trade off recall, latency, index size, and query cost?

## Module 5 — Advanced Retrieval

### Beginner
1. What is query rewriting?
2. What is multi-query retrieval?
3. What is reranking?
4. What is Reciprocal Rank Fusion?

### Intermediate
5. Compare a bi-encoder and a cross-encoder.
6. Explain HyDE and why it can improve retrieval.
7. Compare score fusion with rank fusion.
8. How do candidate count and reranking affect latency and quality?

### Advanced system design
9. Design a hybrid retrieval pipeline with query rewriting, RRF, and reranking.
10. How would you route simple and complex queries to different retrieval strategies?
11. How would you evaluate the contribution and cost of each retrieval stage?

## Module 6 — Advanced RAG

### Beginner
1. What is multi-hop retrieval?
2. What is contextual compression?
3. What is Graph RAG?
4. What is the main idea behind Adaptive RAG?

### Intermediate
5. Compare Self-RAG, Corrective RAG, and Adaptive RAG.
6. When is iterative retrieval better than one-shot retrieval?
7. How does Agentic RAG differ from a conventional RAG pipeline?
8. What problems can knowledge graphs solve in retrieval?

### Advanced system design
9. Design an agentic RAG system for questions that require evidence from multiple documents.
10. Design a Graph RAG pipeline and explain graph construction, retrieval, and grounding.
11. How would you detect retrieval failure and decide whether to search again, reformulate, or abstain?

## Module 7 — Agent Architecture and Orchestration

### Beginner
1. What is tool calling, and what belongs in a tool schema?
2. What is the difference between agent state and memory?
3. What is task decomposition?
4. What is a state machine?

### Intermediate
5. Compare single-agent and multi-agent architectures.
6. Explain supervisor-worker and handoff patterns.
7. When should an agent ask a human for approval?
8. How would you preserve state across a long-running workflow?

### Advanced system design
9. Design a multi-agent research workflow with specialized agents and a coordinator.
10. Design durable orchestration that can resume after a worker or service fails.
11. How would you prevent duplicated actions, conflicting agent outputs, and unbounded delegation?

## Module 8 — Production Engineering

### Beginner
1. What is observability, and why do agents need it?
2. What is the difference between a timeout and a retry?
3. What is caching, and where can it be applied in an AI system?
4. What is a model evaluation regression?

### Intermediate
5. Explain idempotency and why it matters for tool execution.
6. How would you reduce latency and cost in an LLM application?
7. What metrics would you track for an agent in production?
8. How should an agent handle prompt injection in retrieved documents or tool outputs?

### Advanced system design
9. Design a production monitoring and evaluation platform for agent workflows.
10. Design a reliable tool gateway with authentication, authorization, rate limits, audit logs, and failure isolation.
11. How would you scale inference while balancing throughput, latency, quality, and cost?

## Module 9 — End-to-End System Design Projects

### Beginner
1. What requirements should be clarified before designing an enterprise knowledge assistant?
2. What are the main components of an AI customer-support agent?
3. How would you decide whether a project needs RAG, tools, or multiple agents?

### Intermediate
4. Design a research assistant that verifies sources before producing a report.
5. Design a coding assistant that can inspect a repository and propose tested changes.
6. How would you introduce tenant isolation and access control into an enterprise agent?

### Advanced system design
7. Design an end-to-end enterprise knowledge assistant, including ingestion, retrieval, generation, permissions, and monitoring.
8. Design a multi-agent research platform with durable workflows and human review.
9. Given a system with poor answer quality and high latency, how would you diagnose and prioritize improvements?

---

## Company-style practice mapping

Use these as additional framing for the module questions. They are representative practice prompts, not verified company interview questions.

| Company-inspired focus | Relevant modules |
|---|---|
| Google: distributed agents, reliability, search | 1, 4, 5, 8, 9 |
| Meta: scale, ranking, evaluation | 4, 5, 8, 9 |
| Amazon: workflows, authorization, customer support | 1, 7, 8, 9 |
| Microsoft: enterprise RAG, identity, orchestration | 2, 3, 6, 7, 9 |
| OpenAI: tool use, deep research, agent evaluation | 1, 5, 7, 8, 9 |
| Anthropic: safe tool use, coding agents, inference | 1, 7, 8, 9 |
| NVIDIA: inference, GPU scheduling, performance | 3, 8, 9 |

## Per-topic completion checklist

- [ ] Explain the topic without notes.
- [ ] Answer beginner and intermediate questions.
- [ ] Complete at least one advanced design prompt.
- [ ] Draw the architecture and trace a request end to end.
- [ ] Discuss failure modes, security, evaluation, and trade-offs.
- [ ] Implement the core concept and add tests.
