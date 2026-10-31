# Company Case Studies — Hands-on Engineering Track

This directory contains original, runnable educational exercises inspired by **publicly documented** engineering themes. These are not reproductions of proprietary systems and are not verified company interview questions.

## Case-study index

| Organization | Exercise | Architecture focus | Files |
|---|---|---|---|
| OpenAI | Guarded tool-using workflow agent | Tool validation, authorization, approval, idempotency | [Guide](openai/README.md) · [Code](openai/agent.py) · [Tests](openai/test_agent.py) |
| Anthropic | Bounded parallel research workflow | Coordinator, parallel workers, evidence aggregation | [Guide](anthropic/README.md) · [Code](anthropic/agent.py) · [Tests](anthropic/test_agent.py) |
| Google | Context-aware multi-agent analytics | Durable state, artifact references, bounded context | [Guide](google/README.md) · [Code](google/agent.py) · [Tests](google/test_agent.py) |
| Microsoft | Permission-aware enterprise retrieval | Identity, ACL filtering, audit trail | [Guide](microsoft/README.md) · [Code](microsoft/agent.py) · [Tests](microsoft/test_agent.py) |
| AWS | Resilient bounded workflow | Checkpoints, retries, idempotent steps, escalation | [Guide](aws/README.md) · [Code](aws/agent.py) · [Tests](aws/test_agent.py) |
| NVIDIA | Latency-aware inference batch scheduler | Model-compatible batching and throughput/latency trade-offs | [Guide](nvidia/README.md) · [Code](nvidia/agent.py) · [Tests](nvidia/test_agent.py) |

## Standard workflow

Every case study follows the same sequence:

1. **Source analysis** — identify what the public source actually documents and separate it from our interpretation.
2. **Mermaid architecture** — map the request flow, components, state, and trust boundaries.
3. **Component breakdown** — define responsibilities and correctness invariants.
4. **Python implementation** — build a small standard-library reference implementation.
5. **Unit tests** — test expected behavior, invalid inputs, and selected failure cases.
6. **Evaluation plan** — specify measurable quality, reliability, latency, and cost metrics.
7. **Trade-offs and limitations** — state what the design gains, what it costs, and what production still requires.

## Run a case study

Example:

```bash
cd company-practices/openai
python -m unittest -v
```

Repeat in the relevant case-study directory. Python 3.10+ is recommended. No third-party packages are required.

## Important evaluation rule

The included tests validate the educational implementation; they do **not** prove that a design is production-ready or that it matches a company's internal implementation. Evaluation sections are plans, not measured benchmark results. Add real measurements only after running a documented experiment with a stated dataset, environment, and sample size.

## Suggested next additions

- Add structured JSON traces and per-step timing.
- Add integration tests with mocked external services.
- Create a small, versioned evaluation dataset for each workflow.
- Compare a deterministic baseline against an agentic variant.
- Record reproducible latency and cost measurements.
- Add failure injection and security regression tests.
