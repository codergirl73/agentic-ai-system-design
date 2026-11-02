# Module 9 — End-to-End Agentic System Design

**Level:** Advanced  
**Prerequisites:** Modules 1–8  
**Estimated time:** 5–7 hours per project  
**Build:** A complete system design portfolio project with requirements, architecture, APIs, data model, evaluation, implementation plan, and operational trade-offs.

## Learning outcomes

Translate ambiguous requirements into system boundaries, design a complete architecture, estimate scale and cost, define APIs and data contracts, select retrieval and agent patterns, analyze failure modes, and present trade-offs clearly in an interview.

## 1. A repeatable system-design method

~~~mermaid
flowchart TD
    P["Problem and users"] --> R["Requirements and constraints"]
    R --> E["Estimate scale and SLOs"]
    E --> A["High-level architecture"]
    A --> D["Data model and APIs"]
    D --> F["Detailed component flows"]
    F --> S["Security and failure analysis"]
    S --> V["Evaluation and validation"]
    V --> O["Deployment and operations"]
    O --> C["Review trade-offs and iterate"]
~~~

Do not start by drawing boxes. First understand users, tasks, data, permissions, quality requirements, latency, cost, and operational constraints.

## 2. Requirements clarification

Ask:
- Who are the users and what jobs are they trying to complete?
- What sources are trusted and how fresh must they be?
- Are answers advisory or can the system take actions?
- What must be cited or auditable?
- What data is private and who can access it?
- What are the latency, availability, quality, and cost targets?
- What is explicitly out of scope?

Separate functional requirements (what the system does) from non-functional requirements (how well and under what constraints).

## 3. Capacity estimation example

Assume, purely for a design exercise:
- 50,000 registered users;
- 5,000 daily active users;
- 8 requests per active user per day;
- 10 peak requests per second.

Daily requests:

\[
5{,}000 \times 8 = 40{,}000 \text{ requests/day}
\]

Average requests per second:

\[
40{,}000 / 86{,}400 \approx 0.46 \text{ requests/second}
\]

A 10 requests/second peak is about 22 times the average. Capacity planning should use peak and burst patterns, not daily average alone.

## 4. Reference architecture: enterprise knowledge assistant

~~~mermaid
flowchart TD
    U["Web or API client"] --> G["API gateway"]
    G --> I["Authentication and authorization"]
    I --> Q["Query service"]
    Q --> R["Hybrid retrieval"]
    R --> V["Reranker and evidence filter"]
    V --> C["Context builder"]
    C --> M["LLM answer generation"]
    M --> Z["Citation and policy checks"]
    Z --> O["Answer with source links"]
    D["Document sources"] --> P["Ingestion pipeline"]
    P --> X["Parsing and chunking"]
    X --> E["Embedding service"]
    E --> DB["Vector and lexical indexes"]
    DB --> R
    P --> MD["Metadata and version store"]
    MD --> R
~~~

**Request flow**
1. Authenticate the caller.
2. Determine allowed document scope.
3. Retrieve lexical and dense candidates inside that scope.
4. Fuse and rerank candidates.
5. Assemble source text with provenance.
6. Generate an answer constrained to the evidence.
7. Validate citations and disclose missing support.
8. Return the answer and trace the request.

**Ingestion flow**
1. Detect source changes.
2. Parse and normalize content.
3. Chunk with structure and provenance.
4. Generate vectors and lexical records.
5. Publish the new index version.
6. Retire old versions and propagate deletion.

## 5. Data model

A minimal logical model may include:

| Entity | Important fields |
|---|---|
| Document | document_id, tenant_id, version, source_uri, status |
| Chunk | chunk_id, document_id, text, heading, page, offsets |
| Embedding | chunk_id, model_id, dimension, vector |
| Permission | principal_id, document_id, permission |
| Query trace | request_id, query class, selected chunk IDs, latency |
| Feedback | request_id, rating, issue category |

Keep model identity and index version explicit. Do not mix embeddings from incompatible models in one vector search space.

## 6. API contract examples

**Query endpoint**

```http
POST /v1/answers
Content-Type: application/json
Authorization: Bearer <token>
```

```json
{
  "question": "What is the late submission rule?",
  "filters": {"course_id": "CS101"},
  "max_sources": 5
}
```

Possible response:

```json
{
  "answer": "The policy states ...",
  "citations": [
    {
      "document_id": "policy-17",
      "version": "2026-09",
      "section": "Late submissions"
    }
  ],
  "status": "supported",
  "request_id": "req-example"
}
```

The example IDs are illustrative. A real API must define validation, error codes, pagination, authentication, rate limits, and compatibility policy.

## 7. Project A: Enterprise knowledge assistant

**Goal:** Answer employee questions from authorized internal documents.

Key design challenges:
- document permissions and tenant isolation;
- source freshness and versioning;
- citations and auditability;
- hybrid retrieval and reranking;
- no-evidence behavior;
- index update and deletion lifecycle.

**Evaluation:** retrieval Recall@K, answer faithfulness, citation correctness, access-control tests, p95 latency, and cost per query.

## 8. Project B: Research assistant with source verification

**Goal:** Search a defined corpus of research papers, compare methods, and produce a referenced report.

~~~mermaid
flowchart TD
    U["Research request"] --> P["Plan sub-questions"]
    P --> S["Search paper metadata"]
    S --> R["Retrieve paper text"]
    R --> X["Extract claims and methods"]
    X --> C["Build comparison matrix"]
    C --> V["Verify claims against sources"]
    V --> D{"Enough verified evidence?"}
    D -->|Yes| W["Write cited report"]
    D -->|No| S
~~~

Design constraints:
- keep paper metadata and full text provenance;
- distinguish abstract claims from inspected full-text evidence;
- preserve publication versions and dates;
- do not invent missing results;
- cap search and reading budgets.

**Evaluation:** source relevance, claim-to-citation support, coverage of comparison dimensions, duplicate rate, and completion cost.

## 9. Project C: Customer-support assistant

**Goal:** Answer questions using support documentation and route unresolved cases to a human.

Core flow:
1. Identify user and account scope.
2. Retrieve relevant help content.
3. Check whether the answer requires account-specific data.
4. Use only authorized read-only tools by default.
5. Escalate uncertain or consequential cases.
6. Record outcome and feedback.

Measure resolution rate, escalation quality, unsupported-answer rate, latency, and customer satisfaction. Keep policy and account permissions outside model discretion.

## 10. Project D: Coding assistant

**Goal:** Help developers understand a repository and propose changes.

Architecture considerations:
- repository indexing and code-aware chunking;
- symbol and dependency retrieval;
- sandboxed test execution;
- patch review and human approval;
- secret scanning and permission boundaries;
- reproducible test results.

The assistant should distinguish a suggested patch from a verified change. Tests passing in one environment do not prove correctness in all environments.

## 11. Project E: Multi-agent research platform

Use a supervisor with specialist workers only when independent subtasks justify parallelism.

Potential workers:
- source discovery;
- paper reading;
- methodology extraction;
- evidence verification;
- report synthesis.

Define shared state, ownership, deduplication, failure isolation, and a common evidence schema. The supervisor should not accept unsupported worker claims.

## 12. Architecture trade-off matrix

| Decision | Simpler option | More capable option | Trade-off |
|---|---|---|---|
| Retrieval | BM25 | Hybrid + reranker | Quality vs latency/cost |
| Orchestration | Fixed workflow | Dynamic agent | Predictability vs flexibility |
| Deployment | Single service | Distributed services | Simplicity vs independent scaling |
| Storage | One database | Specialized stores | Operational burden vs workload fit |
| Evaluation | Offline test set | Offline + online monitoring | Coverage vs complexity |
| Agents | Single controller | Multi-agent | Coordination overhead vs specialization |

Choose the least complex architecture that satisfies measured requirements.

## 13. Failure analysis

| Failure | User impact | Design response |
|---|---|---|
| Stale index | Old policy returned | Versioning, freshness SLO, rebuild |
| Permission leak | Unauthorized data exposed | Pre-retrieval authorization and tests |
| Retrieval miss | Incomplete answer | Hybrid retrieval, query refinement, abstention |
| Unsupported generation | Incorrect claim | Evidence checks and citation validation |
| Tool outage | Task incomplete | Timeout, fallback, bounded retry |
| Model update regression | Quality drift | Evaluation gate and rollback |
| Cost spike | Budget breach | Per-request budgets and rate limits |

## 14. Interview presentation structure

For a 45-minute design interview:
1. 5 minutes: clarify users, use cases, scope, and constraints.
2. 5 minutes: functional and non-functional requirements.
3. 5 minutes: scale and capacity estimates.
4. 10 minutes: high-level architecture and request/data flows.
5. 10 minutes: deep dive into retrieval, orchestration, data, and APIs.
6. 5 minutes: reliability, privacy, and failure modes.
7. 5 minutes: trade-offs, metrics, and future improvements.

State assumptions clearly. Invite correction before optimizing an assumption that may be wrong.

## 15. Practice design prompts

1. Design an enterprise knowledge assistant for 100,000 documents with per-team access.
2. Design a research assistant that compares five papers and cites every factual claim.
3. Design a customer-support assistant that can retrieve policy but must escalate account changes.
4. Design a codebase assistant for a monorepo with frequent commits.
5. Design a multi-agent analysis workflow and justify why multiple agents are necessary.

For each prompt, produce:
- requirements and assumptions;
- capacity estimates;
- architecture diagram;
- request and ingestion flows;
- API and data model;
- failure and security analysis;
- evaluation plan;
- cost and latency trade-offs.

## 16. Final capstone checklist

- [ ] Clear user problem and explicit scope.
- [ ] Functional and non-functional requirements.
- [ ] Scale and capacity estimates.
- [ ] Architecture and Mermaid diagrams.
- [ ] API contracts and data model.
- [ ] End-to-end request and ingestion flow.
- [ ] Permission and privacy model.
- [ ] Evaluation dataset and metrics.
- [ ] Failure handling and observability.
- [ ] Cost and latency analysis.
- [ ] Runnable implementation or justified prototype.
- [ ] Tests, demo, and design review.

## Further reading

- Designing Data-Intensive Applications — Martin Kleppmann.
- Google Site Reliability Engineering resources.
- BEIR and retrieval evaluation literature.
- ReAct, RAG, Self-RAG, and agent orchestration papers from earlier modules.
