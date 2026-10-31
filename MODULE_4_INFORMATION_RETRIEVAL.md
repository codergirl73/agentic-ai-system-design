# Module 4 — Information Retrieval

**Curriculum:** v1  
**Level:** Intermediate → Advanced  
**Goal:** Understand the architecture, explain design decisions, and implement the core ideas.

## Architecture diagram

```mermaid
flowchart TD
    Q([User query]) --> P[Query preprocessing]
    P --> B[Lexical retrieval: BM25]
    P --> D[Dense retrieval: vector similarity]
    B --> F[Candidate fusion]
    D --> F
    F --> R[Ranked candidate list]
    R --> K[Top-K results]
    K --> E[Evaluate relevance: Recall@K, MRR, NDCG]
    E --> O([Relevant evidence])
    E -->|Poor retrieval| T[Tune analyzers, embeddings, filters, or K]
```

> This is a conceptual reference architecture. Adapt the components and control flow to the system requirements.

---

## Learning outcomes

By completing this module, you should be able to explain each topic below, draw and critique the architecture, implement the core ideas, evaluate the result, and discuss limitations and trade-offs.

## Topics

1. Information retrieval foundations
2. Lexical retrieval and inverted indexes
3. BM25 and sparse retrieval
4. Dense retrieval and vector similarity
5. Keyword vs semantic search
6. Hybrid retrieval
7. Recall@K, Precision@K, MRR, and NDCG

## Implementation milestone

Compare BM25, dense, and hybrid retrieval on an evaluation set.

## System design review checklist

- [ ] Clarify functional and non-functional requirements.
- [ ] Explain the role and responsibility of every component.
- [ ] Walk through a complete request and data flow.
- [ ] Identify trust boundaries, failure modes, and recovery behavior.
- [ ] Discuss latency, throughput, cost, scalability, and trade-offs.
- [ ] Define evaluation metrics and a test strategy.
- [ ] Implement a small working version and document its limitations.

## Interview practice

Use the [module-wise question bank](interview-preparation/MODULE_WISE_QUESTIONS.md) and [company engineering practices](COMPANY_PRACTICES.md) to practice explaining this module from first principles.

## Related resources

- [All architecture diagrams](architecture-diagrams/README.md)
- [Full curriculum](CURRICULUM.md)
- [Company engineering practices](COMPANY_PRACTICES.md)
