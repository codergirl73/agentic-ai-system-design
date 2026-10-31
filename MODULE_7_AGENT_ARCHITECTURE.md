# Module 7 — Agent Architecture and Orchestration

**Curriculum:** v1  
**Level:** Intermediate → Advanced  
**Goal:** Understand the architecture, explain design decisions, and implement the core ideas.

## Architecture diagram

```mermaid
flowchart TD
    U([Task request]) --> O[Supervisor / orchestrator]
    O --> P[Plan and decompose task]
    P --> S[(Shared task state)]
    S --> W1[Worker agent: research]
    S --> W2[Worker agent: analysis]
    S --> W3[Worker agent: synthesis]
    W1 --> G[Tool gateway]
    W2 --> G
    W3 --> G
    G --> V[Validate schema, policy, and permissions]
    V --> T[Approved tools and services]
    T --> S
    S --> C[Aggregate and evaluate results]
    C --> H{Human approval required?}
    H -->|Yes| A[Human review]
    H -->|No| F([Final result])
    A --> F
```

> This is a conceptual reference architecture. Adapt the components and control flow to the system requirements.

---

## Learning outcomes

By completing this module, you should be able to explain each topic below, draw and critique the architecture, implement the core ideas, evaluate the result, and discuss limitations and trade-offs.

## Topics

1. Tool calling and tool schemas
2. Planning and task decomposition
3. State, memory, and context management
4. Reflection and critique patterns
5. Workflow orchestration and state machines
6. Single-agent architectures
7. Multi-agent systems
8. Supervisor-worker and handoff patterns
9. Human-in-the-loop approval

## Implementation milestone

Build a stateful workflow with typed tools and human approval for consequential actions.

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
