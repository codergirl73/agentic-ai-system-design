# Module 7 — Agent Architecture and Orchestration

**Curriculum:** v1  
**Level:** Intermediate → Advanced  
**Goal:** Understand the architecture, explain design decisions, and implement the core ideas.

## Architecture diagram

An orchestration layer coordinates agent reasoning, tools, memory, specialist workers, and human approval.

![Module 7 — Agent Architecture and Orchestration architecture](architecture-diagrams/module-7.svg)

[Open the full-size SVG](architecture-diagrams/module-7.svg).

> Diagram flow: Task request → supervisor/planner → state and memory / worker agents → tool gateway → services → approval and result aggregation.  
> This is a conceptual reference architecture. Adapt components and control flow to the system requirements; it is not a mandatory implementation blueprint.

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
