# Module 8 — Production Engineering for Agentic Systems

**Level:** Intermediate → Advanced  
**Prerequisites:** Modules 1–7  
**Estimated time:** 4–5 hours  
**Build:** A production-readiness plan with evaluation, tracing, reliability controls, cost budgets, and security boundaries.

## Learning outcomes

Design evaluation and observability, reason about latency and throughput, use timeouts and bounded retries, plan caching and model routing, secure tool access, protect data, deploy safely, and respond to incidents.

## 1. From prototype to production

A prototype demonstrates that a task can work once. A production system must work predictably across many requests, handle failures, protect data, and stay within service-level targets.

~~~mermaid
flowchart TD
    U["Client request"] --> A["API and authentication"]
    A --> P["Policy and budget checks"]
    P --> R["Agent or RAG runtime"]
    R --> G["Model and tool gateway"]
    G --> X["Models and external services"]
    X --> R
    R --> T["Traces and metrics"]
    T --> E["Evaluation and regression"]
    E --> M["Monitoring and alerts"]
    M --> I["Incident response and improvement"]
~~~

## 2. Define requirements and service objectives

Separate functional requirements from non-functional requirements.

| Type | Example |
|---|---|
| Functional | Answer questions with source citations |
| Quality | At least a target fraction of claims supported |
| Latency | p95 response under a chosen budget |
| Availability | Defined monthly availability objective |
| Cost | Average and maximum cost per request |
| Security | Enforce tenant and document permissions |
| Freshness | Reflect approved source updates within a defined interval |

A service-level indicator (SLI) is a measured quantity. A service-level objective (SLO) is a target for that quantity. A service-level agreement (SLA) is a formal commitment. Do not confuse them.

## 3. Evaluation strategy

Use multiple layers:
- unit tests for deterministic functions;
- integration tests for service boundaries;
- regression tests for known cases;
- offline quality evaluation on labelled datasets;
- online monitoring and user feedback;
- adversarial and permission tests.

A useful evaluation set includes normal, ambiguous, long, multilingual, no-evidence, conflicting-source, and malformed-input cases.

## 4. Observability: logs, metrics, and traces

~~~mermaid
flowchart TD
    R["One request"] --> T["Distributed trace"]
    T --> S["Step spans"]
    S --> L["Structured logs"]
    S --> M["Metrics"]
    M --> A["Dashboards and alerts"]
    L --> D["Debugging"]
    A --> I["Incident response"]
~~~

- **Logs** describe discrete events.
- **Metrics** aggregate numeric behavior over time.
- **Traces** connect work across components and show where time was spent.

For an agent run, record run ID, stage, model/tool name, duration, status, retry count, and budget remaining. Redact secrets and avoid logging unnecessary personal content.

## 5. Reliability patterns

### Timeouts

Every network and model call needs a deadline. A timeout should release resources and produce a structured error.

### Retries and backoff

Retry transient failures, not every failure. Use exponential backoff with jitter and a maximum attempt count. Do not retry invalid arguments or permission denials as if they were network errors.

### Idempotency

If a client retries a request, an idempotency key can prevent duplicate side effects. The receiver must store and check the key consistently.

### Circuit breakers

When a dependency repeatedly fails, stop sending it traffic temporarily, fail fast or use a fallback, then probe for recovery.

~~~mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: failure threshold reached
    Open --> HalfOpen: cooldown elapsed
    HalfOpen --> Closed: probe succeeds
    HalfOpen --> Open: probe fails
~~~

## 6. Latency and throughput

Total latency includes queueing, model calls, retrieval, tools, reranking, and response serialization.

A sequential workflow adds stage latencies. Parallel independent tasks may reduce wall-clock time, but consume more concurrent resources. Measure p50, p95, and p99 rather than only the average.

Throughput is requests completed per unit time. Capacity planning must include concurrency limits, model rate limits, queue depth, and downstream service capacity.

## 7. Cost optimization

Cost drivers may include input/output tokens, embedding generation, reranking, tool calls, storage, and network egress.

Useful techniques:
- cache stable retrieval results with explicit freshness rules;
- route simple tasks to smaller models when quality permits;
- cap context size and candidate counts;
- batch offline embedding jobs;
- avoid redundant agent loops;
- track cost by request and task class.

Never optimize cost by silently removing required safety or evidence checks.

## 8. Security boundaries

~~~mermaid
flowchart TD
    U["Untrusted user and document content"] --> R["Agent runtime"]
    R --> P["Policy enforcement"]
    P --> V["Validate tool and arguments"]
    V --> A["Authorization check"]
    A -->|Allowed| T["Narrowly scoped tool"]
    A -->|Denied| D["Reject and audit"]
    T --> O["Verify result"]
~~~

Core controls:
- authenticate the caller;
- authorize each document and tool action;
- use least-privilege credentials;
- treat retrieved content and tool output as untrusted data;
- separate instructions from data;
- validate structured arguments;
- constrain network and filesystem access;
- record security-relevant decisions;
- test prompt-injection and data-exfiltration scenarios safely.

A model's decision is not an authorization mechanism. Enforce permissions in application code and downstream services.

## 9. Privacy and data lifecycle

Classify data, minimize collection, encrypt in transit and at rest, restrict access, define retention and deletion, and ensure derived indexes follow source permissions and deletion requests. Do not place credentials or private tokens in prompts or logs.

For multi-tenant retrieval, apply access filters before content is exposed to the model. Test that a user cannot retrieve another tenant's passages even when the query is crafted to target them.

## 10. Deployment and release strategy

A reliable release process includes:
1. automated tests and static checks;
2. evaluation against a fixed regression set;
3. staged rollout;
4. health and quality monitoring;
5. rollback plan;
6. index and schema compatibility checks.

Canary releases expose a small share of traffic to a new version before wider rollout. Shadow evaluation can compare outputs without showing the new result to users, subject to privacy and data-handling controls.

## 11. Python: retry only transient failures

```python
import random
import time


class TransientError(Exception):
    pass


def call_with_retry(operation, max_attempts=3, base_delay=0.05, sleep=time.sleep):
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")

    for attempt in range(max_attempts):
        try:
            return operation()
        except TransientError:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt)
            sleep(delay + random.uniform(0, delay * 0.1))
```

This simplified example retries only a declared transient exception. Production code should use request deadlines, cancellation, bounded total time, structured error types, and observability.

## 12. Unit tests

```python
import unittest
from reliability import TransientError, call_with_retry


class RetryTests(unittest.TestCase):
    def test_succeeds_after_transient_failure(self):
        calls = {"count": 0}

        def operation():
            calls["count"] += 1
            if calls["count"] == 1:
                raise TransientError()
            return "ok"

        result = call_with_retry(operation, sleep=lambda _: None)
        self.assertEqual(result, "ok")
        self.assertEqual(calls["count"], 2)

    def test_stops_after_attempt_limit(self):
        calls = {"count": 0}

        def operation():
            calls["count"] += 1
            raise TransientError()

        with self.assertRaises(TransientError):
            call_with_retry(operation, max_attempts=2, sleep=lambda _: None)
        self.assertEqual(calls["count"], 2)

    def test_does_not_retry_other_errors(self):
        calls = {"count": 0}

        def operation():
            calls["count"] += 1
            raise ValueError("invalid request")

        with self.assertRaises(ValueError):
            call_with_retry(operation, sleep=lambda _: None)
        self.assertEqual(calls["count"], 1)


if __name__ == "__main__":
    unittest.main()
```

## 13. Incident example

A new retrieval index causes p95 latency to double and citation quality to fall.

A disciplined response:
1. Detect the regression from latency and quality dashboards.
2. Identify the release and affected request cohorts.
3. Roll back or route traffic to the last known-good index.
4. Preserve traces and representative failures.
5. Compare index settings and evaluation results.
6. Add a regression test before redeployment.

## 14. Failure modes

| Failure | Likely cause | Control |
|---|---|---|
| Retry storm | Unbounded retries | Backoff, jitter, attempt and deadline caps |
| Duplicate side effect | Client retries non-idempotent call | Idempotency keys and verification |
| Silent quality regression | Only infrastructure metrics monitored | Quality regression set and online review |
| Cross-tenant data leak | Authorization after retrieval or absent | Enforce permission filters before exposure |
| Cost spike | Context, loops, or concurrency grew | Per-request budgets and dashboards |
| Hard-to-debug run | No trace correlation | Run IDs and structured spans |

## 15. Interview walkthrough

**Prompt:** A document assistant is accurate in tests but becomes slow and expensive after launch.

1. Segment latency by stage and inspect p50/p95/p99.
2. Check query mix, context size, retrieval candidates, reranking, model routing, and retries.
3. Track cost per request class and cache hit rate.
4. Check queueing and downstream rate limits.
5. Optimize one bottleneck at a time.
6. Re-run quality tests to ensure savings do not reduce answer support.
7. Use staged rollout and rollback.

## 16. Practice

### MCQs

1. A trace is most useful for:
   - A. Connecting stages of one request
   - B. Replacing authorization
   - C. Storing model weights
   - D. Guaranteeing factuality

2. Idempotency helps prevent:
   - A. Duplicate side effects on repeated requests
   - B. All model hallucinations
   - C. Every timeout
   - D. Every retrieval miss

3. Authorization should be enforced:
   - A. Only by asking the model
   - B. In application and downstream service boundaries
   - C. After exposing all retrieved content
   - D. Only in documentation

### Short-answer questions

1. Distinguish logs, metrics, and traces.
2. Explain why retries need a deadline and backoff.
3. What does p95 latency mean?
4. Why is a model not an authorization system?
5. Name two privacy controls for a multi-tenant RAG system.

### Answer key

**MCQs:** 1-A, 2-A, 3-B.

**Short answers:**
1. Logs are event records, metrics are aggregate measurements, and traces connect stages of a request.
2. To avoid retry storms and keep total time bounded during dependency failures.
3. 95 percent of measured requests completed at or below that latency.
4. Model output is probabilistic and untrusted; permissions must be enforced deterministically by the application.
5. Tenant-aware retrieval filters, least privilege, encryption, retention controls, and audit logging.

## 17. Mini-project and completion checklist

Write a production-readiness design for a multi-tenant RAG assistant. Include SLOs, evaluation plan, trace schema, retry policy, cost budget, access controls, rollout and rollback.

- [ ] Define functional and non-functional requirements.
- [ ] Design logs, metrics, and traces.
- [ ] Set deadlines, retries, and idempotency behavior.
- [ ] Estimate latency and cost by stage.
- [ ] Define tenant authorization and data lifecycle.
- [ ] Create a regression and rollback plan.

## Further reading

- Google SRE Workbook and Site Reliability Engineering resources.
- OpenTelemetry documentation for traces, metrics, and logs.
- OWASP guidance for LLM application risks.
