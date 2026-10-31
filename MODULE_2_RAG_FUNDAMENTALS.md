# Module 2 — RAG Fundamentals

**Curriculum:** v1  
**Level:** Intermediate → Advanced  
**Goal:** Understand the architecture, explain design decisions, and implement the core ideas.

## Architecture diagram

A retrieval-augmented generation pipeline grounds model responses in retrieved evidence.

![Module 2 — RAG Fundamentals architecture](architecture-diagrams/module-2.svg)

[Open the full-size SVG](architecture-diagrams/module-2.svg).

> Diagram flow: User question → query processing → retriever → relevant passages → context assembly → LLM → answer with citations.  
> This is a conceptual reference architecture. Adapt components and control flow to the system requirements; it is not a mandatory implementation blueprint.

---

## Learning outcomes

By completing this module, you should be able to explain each topic below, draw and critique the architecture, implement the core ideas, evaluate the result, and discuss limitations and trade-offs.

## Topics

1. What RAG is and why it is used
2. RAG vs fine-tuning vs long-context prompting
3. Ingestion and query-time stages
4. Retrieval, context assembly, and generation
5. Source attribution, grounding, and failure modes

## Implementation milestone

Build document Q&A that returns answers with source references.

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
