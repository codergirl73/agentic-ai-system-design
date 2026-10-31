# Company Engineering Practices for Agentic AI System Design

A central, evidence-based collection of **publicly documented engineering practices, architecture patterns, and system-design exercises** from leading technology and AI organizations.

> Scope note: This repository studies public engineering articles, documentation, talks, and reference architectures. It does not claim access to confidential internal systems or reproduce private interview questions. Company-inspired exercises below are original practice prompts, not verified interview questions.

## How to use this hub

For each organization:
1. Read the primary source and record its publication/update date.
2. Extract the system problem, architecture, control flow, data/context strategy, and operational constraints.
3. Recreate the architecture in your own diagram.
4. Implement a small, testable version in Python.
5. Evaluate reliability, quality, latency, cost, security, and maintainability.
6. Write a short design review: what you would keep, change, and why.

## Company practice library

### Anthropic
**Themes to study**
- Multi-agent research: planning, parallel sub-agents, tool design, coordination, evaluation, and reliability.
- Effective harnesses for long-running agents and coding workflows.
- Context engineering and advanced tool use.
- Safety boundaries and permission-aware tool execution.

**Primary reading**
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic Engineering](https://www.anthropic.com/engineering)

**Practice exercise — Deep research agent**
Design a research agent that decomposes a question, launches bounded parallel research workers, collects cited evidence, resolves conflicting findings, and produces a verifiable report. Specify worker limits, source quality rules, shared state, timeouts, and evaluation.

### OpenAI
**Themes to study**
- Tool-using and long-running agent workflows.
- Agent orchestration, handoffs, and reliable tool execution.
- Evaluation of agent behavior and end-to-end task success.
- Model/tool boundaries, structured outputs, and operational controls.

**Primary reading**
- [OpenAI developer platform documentation](https://platform.openai.com/docs)
- [OpenAI Research](https://openai.com/research/)

**Practice exercise — Tool-using workflow agent**
Design an assistant that can plan a multi-step task and call a small set of external tools. Define tool schemas, authorization checks, idempotency, retries, trace events, and a human approval point for consequential actions. Treat model-generated tool requests as proposals, not trusted commands.

### Google
**Themes to study**
- Single-agent and multi-agent reference architectures.
- Agent Development Kit (ADK) and context engineering.
- Separating durable session state, memory, artifacts, and per-call working context.
- Enterprise integration and orchestration patterns.

**Primary reading**
- [Google Cloud: Agentic AI architecture guides](https://docs.cloud.google.com/architecture/agentic-ai-overview)
- [Architecting an efficient context-aware multi-agent framework for production](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/)

**Practice exercise — Context-aware multi-agent analytics**
Design a system with a coordinator and specialist agents for data discovery, analysis, and report generation. Define what state is durable, what enters each model call, how artifacts are referenced, and how context is trimmed and audited.

### Microsoft
**Themes to study**
- Enterprise multi-agent collaboration.
- Identity, access control, data protection, evaluations, and governance.
- Moving from prototype to production with developer tooling and observability.

**Primary reading**
- [Designing Multi-Agent Intelligence](https://developer.microsoft.com/en-us/blog/designing-multi-agent-intelligence/)
- [Agent Factory: blueprint for safe and secure AI agents](https://azure.microsoft.com/en-us/blog/agent-factory-creating-a-blueprint-for-safe-and-secure-ai-agents/)
- [Agent Factory: prototype to production](https://azure.microsoft.com/en-us/blog/agent-factory-from-prototype-to-production-developer-tools-and-rapid-agent-development/)

**Practice exercise — Permission-aware enterprise assistant**
Design an enterprise assistant that searches multiple business systems while enforcing the requesting user's permissions. Explain identity propagation, retrieval-time authorization, audit logs, data isolation, and how permissions are checked again before an action.

### Amazon Web Services (AWS)
**Themes to study**
- Well-Architected principles for agentic workloads.
- Reliability, security, operational excellence, performance, cost, and sustainability.
- Agent identity, least privilege, bounded autonomy, observability, and human oversight.
- Resilience patterns for nondeterministic agent workflows.

**Primary reading**
- [AWS Well-Architected Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html)
- [Build resilient generative AI agents](https://aws.amazon.com/blogs/architecture/build-resilient-generative-ai-agents/)
- [System design and security recommendations for agentic AI systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-security/best-practices-system-design.html)

**Practice exercise — Resilient customer-support agent**
Design an agent that can answer questions and initiate a limited set of support workflows. Include least-privilege tools, deterministic validation, bounded retries, idempotency, fallback to a human, per-task cost budgets, and operational dashboards.

### NVIDIA
**Themes to study**
- Inference serving and optimization.
- GPU scheduling, throughput, latency, batching, and model deployment.
- Data/embedding pipelines and scalable AI infrastructure.

**Primary reading**
- [NVIDIA Technical Blog](https://developer.nvidia.com/blog/)
- [NVIDIA Developer Documentation](https://docs.nvidia.com/)

**Practice exercise — Agent inference platform**
Design an inference platform serving multiple agent workloads with different latency and throughput needs. Discuss model routing, batching, queueing, GPU utilization, isolation, autoscaling, and cost attribution. Validate choices with measurements rather than assumptions.

## Hands-on implementation case studies

Runnable exercises are maintained separately under [`company-practices/`](company-practices/README.md). Each includes source analysis, Mermaid architecture, component responsibilities, Python implementation, unit tests, an evaluation plan, and design trade-offs.

- [Open the hands-on case-study index](company-practices/README.md)

## Cross-company architecture patterns to compare

| Design question | Patterns to investigate |
|---|---|
| How much autonomy? | Deterministic workflow, single agent, supervisor-worker, multi-agent |
| How are tools controlled? | Typed schemas, allowlists, scoped identity, authorization, approval gates |
| How is context managed? | Working context, session state, long-term memory, artifacts, retrieval |
| How is work coordinated? | Sequential handoff, parallel workers, shared state, message passing |
| How is quality measured? | Task success, groundedness, tool correctness, human review, regression evals |
| How does the system recover? | Timeouts, bounded retries, idempotency, checkpoints, fallbacks |
| How is production behavior understood? | Traces, structured events, metrics, evaluation dashboards |
| How is cost controlled? | Token budgets, model routing, caching, concurrency limits, per-task budgets |

## Reusable company case-study template

Copy this template for each new company or public engineering article.

### Source
- Organization:
- Article / documentation title:
- URL:
- Publication or last-updated date:
- Source type: official engineering article / official documentation / talk / open-source repository

### Problem and requirements
- User or business problem:
- Functional requirements:
- Non-functional requirements:
- Scale assumptions:

### Architecture
- Main components:
- Agent roles and responsibilities:
- Orchestration pattern:
- Tool/API boundaries:
- Data, memory, and context flow:
- Human approval points:

### Runtime behavior
- End-to-end request flow:
- State transitions:
- Failure handling and recovery:
- Security and authorization boundaries:

### Evaluation and operations
- Quality metrics:
- Reliability metrics:
- Latency and cost considerations:
- Observability:
- Known limitations / unanswered questions:

### My analysis
- What is reusable?
- What would I change?
- What trade-offs are being made?
- What small implementation will I build?
- What tests will demonstrate correctness?

## Suggested implementation backlog

- [ ] Recreate a bounded tool-using agent with schema validation and an allowlist.
- [ ] Build a parallel research workflow with worker limits and evidence aggregation.
- [ ] Implement a context manager that separates session history, memory, and working context.
- [ ] Build permission-aware retrieval with user-scoped document access.
- [ ] Add tracing, evaluation datasets, and regression tests to an agent workflow.
- [ ] Compare a deterministic workflow, a single agent, and a multi-agent design on the same task.

## Research and attribution standards

- Prefer primary sources from the organization itself.
- Record the date because engineering guidance changes.
- Separate what the source explicitly states from your own interpretation.
- Do not infer proprietary implementation details from product behavior.
- Do not label an exercise as an actual company interview question unless the company has publicly confirmed it.
- Link to papers and documentation; do not upload copyrighted material without permission.

---

*This is a living study index. Add a new case study when you have read the source, documented the architecture, and completed your own trade-off analysis.*
