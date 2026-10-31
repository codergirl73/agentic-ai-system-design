# Module 5 — Advanced Retrieval

**Curriculum:** v1  
**Level:** Intermediate → Advanced  
**Goal:** Understand the architecture, explain design decisions, and implement the core ideas.

## Architecture diagram

```mermaid
flowchart TD
    Q([User query]) --> A[Rewrite / decompose query]
    A --> B[Generate multiple queries]
    A --> H[Optional HyDE representation]
    B --> R[Retrieve candidates]
    H --> R
    R --> F[Merge rankings with RRF or score fusion]
    F --> X[Cross-encoder reranking]
    X --> K[Select top-K passages]
    K --> C([Context for generation])
    X --> M[Measure relevance and latency]
```

> This is a conceptual reference architecture. Adapt the components and control flow to the system requirements.

---

## Learning outcomes

By completing this module, you should be able to explain each topic below, draw and critique the architecture, implement the core ideas, evaluate the result, and discuss limitations and trade-offs.

## Topics

1. Query rewriting and normalization
2. Multi-query retrieval
3. Query expansion and decomposition
4. HyDE
5. Reranking: bi-encoders vs cross-encoders
6. Reciprocal Rank Fusion (RRF)
7. Score fusion and rank fusion
8. Candidate generation, top-K selection, and latency trade-offs

## Implementation milestone

Build multi-query retrieval with RRF and reranking; evaluate each stage.

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
