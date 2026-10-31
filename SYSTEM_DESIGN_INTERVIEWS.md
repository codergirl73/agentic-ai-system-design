# Company-Style System Design Interview Practice

These are **representative practice prompts** inspired by common engineering problem areas at major technology and AI companies. They are not verified questions from actual company interviews.

## Google-style practice — agent architecture and reliability
1. Design an AI research assistant that searches multiple sources and produces a cited report.
2. Design an agent that investigates production incidents using logs and monitoring data.
3. Design a real-time voice assistant that supports interruptions.
4. Design a tool-execution service with timeouts, retries, and failure recovery.

**Study areas:** distributed services, planning, tool orchestration, latency, reliability, observability.

## Meta-style practice — scale and recommendation systems
1. Design an AI content-understanding pipeline for a large social platform.
2. Design an assistant integrated into a messaging product.
3. Design a recommendation agent that learns from user interactions.
4. Design an evaluation platform for high-volume model predictions.

**Study areas:** throughput, distributed processing, caching, evaluation, cost.

## Amazon-style practice — automation and customer experience
1. Design a customer-support agent that resolves routine requests.
2. Design a shopping assistant that compares products against user constraints.
3. Design an order-status agent that interacts with multiple backend services.
4. Design authorization and approval controls for agent-initiated actions.

**Study areas:** APIs, workflow orchestration, permissions, idempotency, human approval.

## Microsoft-style practice — enterprise AI and RAG
1. Design an enterprise knowledge assistant across documents and collaboration tools.
2. Design permission-aware retrieval for a multi-tenant organization.
3. Design a conversational analytics agent over structured business data.
4. Design a multi-agent workflow for specialized enterprise tasks.

**Study areas:** RAG, identity, access control, connectors, memory, multi-tenancy.

## OpenAI-style practice — LLM products and agent workflows
1. Design a deep-research agent that produces a cited report.
2. Design an assistant that uses tools and maintains context over long tasks.
3. Design a scalable conversational AI application.
4. Design an evaluation platform for agent task success and regressions.
5. Design durable execution for long-running tasks that can resume after failure.

**Study areas:** context management, tool calling, streaming, durable workflows, evaluation.

## Anthropic-style practice — inference and safe tool use
1. Design a coding agent that can inspect a codebase, propose changes, and run tests.
2. Design a safe tool interface for an AI assistant.
3. Design a high-throughput LLM inference API.
4. Design a reliable service for distributing and caching large model artifacts.

**Study areas:** inference, batching, infrastructure, security boundaries, reliability.

## NVIDIA-style practice — AI infrastructure and performance
1. Design a distributed LLM inference platform.
2. Design a GPU scheduling service shared by multiple AI workloads.
3. Design an embedding-generation service for millions of documents.
4. Design a model router that balances latency, quality, and cost.

**Study areas:** GPU utilization, batching, memory, concurrency, scheduling, inference performance.

---

## Universal system design answer framework

1. **Requirements:** clarify users, use cases, scope, and constraints.
2. **Scale:** estimate traffic, data volume, concurrency, latency, and cost.
3. **Architecture:** draw the major components and their connections.
4. **Interfaces:** define key APIs, events, and data models.
5. **Data flow:** trace one request end to end.
6. **Reliability:** discuss timeouts, retries, idempotency, fallbacks, and recovery.
7. **Security:** cover authentication, authorization, privacy, and tool boundaries.
8. **Operations:** explain evaluation, observability, deployment, and monitoring.
9. **Trade-offs:** compare alternatives and justify the chosen design.

## How to practice each prompt

For each question, prepare:
- A 5-minute requirements discussion.
- A high-level architecture diagram.
- A detailed component walkthrough.
- One end-to-end request flow.
- Three failure scenarios and mitigations.
- Two scaling bottlenecks.
- Three interviewer follow-up questions.
- A concise explanation of major trade-offs.
