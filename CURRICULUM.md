# Curriculum — Agentic AI System Design

## Module 1 — Foundations of Agentic AI
1. What is an AI agent?
2. AI model vs chatbot vs AI agent
3. What makes a system agentic?
4. Agents, tools, memory, and planning
5. Agent execution loop: observe, reason, act, and evaluate
6. Stopping conditions, iteration limits, and failure handling
**Implementation milestone:** Build a minimal goal-oriented Python agent, then extend it with a tool and bounded execution loop.

## Module 2 — RAG Fundamentals
1. What is Retrieval-Augmented Generation (RAG)?
2. Why RAG: freshness, grounding, and provenance
3. RAG vs fine-tuning vs long-context prompting
4. Basic RAG architecture
5. Retrieval and generation stages
6. Sources, citations, and grounded answers
**Implementation milestone:** Build document Q&A with source references.

## Module 3 — Document Processing and Embeddings
1. Document ingestion and parsing
2. Cleaning, normalization, and metadata
3. Chunking strategies and overlap
4. Embeddings and semantic representation
5. Vector indexes and vector databases
6. Metadata filtering and index lifecycle
7. Embedding evaluation and failure modes
**Implementation milestone:** Build configurable ingestion, chunking, embedding, and indexing.

## Module 4 — Information Retrieval
1. Information retrieval foundations
2. Lexical retrieval and inverted indexes
3. BM25 and sparse retrieval
4. Dense retrieval and vector similarity
5. Keyword vs semantic search
6. Hybrid retrieval
7. Recall@K, Precision@K, MRR, and NDCG
**Implementation milestone:** Compare BM25, dense, and hybrid retrieval on an evaluation set.

## Module 5 — Advanced Retrieval
1. Query rewriting and normalization
2. Multi-query retrieval
3. Query expansion and decomposition
4. HyDE
5. Reranking: bi-encoders vs cross-encoders
6. Reciprocal Rank Fusion (RRF)
7. Score fusion and rank fusion
8. Candidate generation, top-K selection, and latency trade-offs
**Implementation milestone:** Build multi-query retrieval with RRF and reranking; evaluate each stage.

## Module 6 — Advanced RAG
1. Context assembly and contextual compression
2. Multi-hop and iterative retrieval
3. Self-RAG
4. Corrective RAG (CRAG)
5. Adaptive RAG
6. Agentic RAG
7. Graph RAG and knowledge graphs
8. RAG evaluation and error analysis
**Implementation milestone:** Build and evaluate an advanced RAG workflow.

## Module 7 — Agent Architecture and Orchestration
1. Tool calling and tool schemas
2. Planning and task decomposition
3. State, memory, and context management
4. Reflection and critique patterns
5. Workflow orchestration and state machines
6. Single-agent architectures
7. Multi-agent systems
8. Supervisor-worker and handoff patterns
9. Human-in-the-loop approval
**Implementation milestone:** Build a stateful workflow with typed tools and human approval for consequential actions.

## Module 8 — Production Engineering
1. Evaluation datasets and offline evaluation
2. Tracing, observability, and debugging
3. Reliability, retries, timeouts, and fallbacks
4. Latency, throughput, and cost optimization
5. Caching and model routing
6. Security boundaries and prompt-injection risks
7. Data privacy and access control
8. Deployment, monitoring, and regression testing
**Implementation milestone:** Add tests, traces, metrics, bounded retries, security checks, and deployment documentation.

## Module 9 — End-to-End System Design Projects
1. Enterprise knowledge assistant
2. Research assistant with source verification
3. Customer-support agent
4. Coding assistant
5. Multi-agent research platform
6. Design reviews: requirements, architecture, APIs, data flow, failure modes, and trade-offs
**Implementation milestone:** Complete an end-to-end project with architecture documentation, evaluation report, tests, and demo.

## Topic completion standard
A topic is complete when you can explain it from first principles, draw its architecture, implement and test its core idea, answer interview questions, discuss limitations and trade-offs, and identify relevant research when meaningful.
