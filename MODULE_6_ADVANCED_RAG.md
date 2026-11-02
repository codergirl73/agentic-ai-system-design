# Module 6 — Advanced RAG: Adaptive, Iterative and Structured Retrieval

**Level:** Intermediate → Advanced  
**Prerequisites:** Modules 2–5  
**Estimated time:** 4–5 hours  
**Build:** An evidence-aware RAG workflow that can retrieve again when support is weak and stop when its budget is exhausted.

## Learning outcomes

Explain contextual compression, multi-hop retrieval, adaptive retrieval, corrective retrieval, self-reflection patterns, graph-based retrieval, agentic RAG, and advanced RAG evaluation. Distinguish useful control loops from unnecessary complexity.

## 1. Why basic RAG is not enough

A simple RAG pipeline retrieves once and generates once. That works for direct questions, but more difficult questions may need:
- several documents;
- intermediate facts to form a follow-up query;
- filtering of irrelevant passages;
- explicit evidence sufficiency checks;
- a safe response when the corpus cannot answer.

Example: "Which policy applies to a student who has an approved extension and submits after the revised deadline?" The answer may require combining the general late rule with the extension rule.

## 2. Advanced RAG architecture

~~~mermaid
flowchart TD
    Q["User question"] --> I["Classify query and complexity"]
    I --> S["Choose retrieval strategy"]
    S --> R["Retrieve candidate evidence"]
    R --> G["Grade relevance and coverage"]
    G --> D{"Evidence sufficient?"}
    D -->|Yes| C["Compress and assemble context"]
    C --> A["Generate cited answer"]
    A --> V["Verify claim support"]
    V -->|Supported| O["Return answer"]
    V -->|Weak support| W["Bounded query refinement"]
    D -->|No| W
    W --> B{"Retry budget remains?"}
    B -->|Yes| R
    B -->|No| U["Return uncertainty and evidence gap"]
~~~

A control loop must have a bounded retry count, time budget, and clear stopping conditions. Repeated retrieval is not automatically better.

## 3. Contextual compression

Retrieval may return long passages containing only a small relevant sentence. Contextual compression selects or summarizes relevant spans before generation.

**Before compression**

A two-page policy section contains submission rules, grading rules, office hours, and contact details.

**After compression**

- Relevant rule: late work loses 10 percent per calendar day.
- Exception: approved extensions use the revised deadline.
- Provenance: document version, section, page.

Compression can reduce token usage and noise, but careless summarization may remove qualifiers or exceptions. Preserve source spans and verify compressed statements against originals.

## 4. Multi-hop retrieval

Multi-hop questions require an intermediate result to retrieve the next evidence.

~~~mermaid
flowchart TD
    Q["Question requiring two facts"] --> R1["Retrieve first evidence"]
    R1 --> F["Extract intermediate entity or condition"]
    F --> Q2["Form follow-up query"]
    Q2 --> R2["Retrieve second evidence"]
    R2 --> J["Join evidence with provenance"]
    J --> A["Answer with both citations"]
~~~

Example:
1. Find the policy defining the revised deadline.
2. Use that deadline condition to find the rule governing late submissions after an extension.
3. Combine both passages and cite each one.

The system should track which claims depend on which passages. If the second hop fails, state that the answer is incomplete rather than filling the gap with assumptions.

## 5. Adaptive RAG

Adaptive RAG selects a retrieval strategy based on query complexity, freshness requirements, and evidence availability.

| Query type | Possible route |
|---|---|
| Simple known fact | One retrieval pass |
| Exact identifier | Lexical search |
| Paraphrased question | Dense or hybrid search |
| Multi-part comparison | Query decomposition |
| Evidence missing | Bounded retry or clarification |
| No trusted source | State limitation |

A classifier can make mistakes. Keep a safe default route and log the chosen strategy so routing decisions can be evaluated.

## 6. Corrective RAG pattern

A corrective retrieval workflow evaluates retrieved evidence. If the evidence appears weak, it may rewrite the query, search another source, or return an evidence gap.

~~~mermaid
flowchart TD
    Q["Question"] --> R["Retrieve"]
    R --> J["Judge relevance and coverage"]
    J --> D{"Good evidence?"}
    D -->|Yes| G["Generate grounded answer"]
    D -->|No| X["Rewrite or broaden search"]
    X --> R
    G --> V["Verify citations"]
    V --> O["Answer or disclose limitation"]
~~~

A relevance grader is itself fallible. It should not be treated as a truth oracle. Test false positives (bad evidence judged good) and false negatives (useful evidence judged bad).

## 7. Self-reflective retrieval patterns

Some RAG designs let a model decide whether retrieval is needed, critique evidence, or revise a draft. These patterns can improve control, but can also add model calls and create self-confirming errors.

Useful checks:
- Is retrieval needed for this query?
- Does each claim have a supporting passage?
- Is there contradictory evidence?
- Is the evidence current and authorized?
- Is another retrieval attempt likely to add information?

A model's confidence statement is not a substitute for evidence evaluation.

## 8. Graph RAG and knowledge graphs

A knowledge graph represents entities and relationships explicitly.

~~~mermaid
flowchart LR
    S["Source documents"] --> E["Entity and relation extraction"]
    E --> G["Knowledge graph"]
    Q["User query"] --> X["Entity linking"]
    X --> P["Graph traversal"]
    G --> P
    P --> C["Relevant nodes and source passages"]
    C --> A["Grounded synthesis"]
~~~

Example triples:
- Course A — has_policy — Late Submission Policy
- Late Submission Policy — defines — Daily Deduction
- Approved Extension — changes — Due Date

Graph structure can help with relationships and multi-hop questions. Extraction errors, entity ambiguity, graph maintenance, and incomplete relationships are important risks. Keep links back to source passages; a graph fact without provenance is hard to verify.

## 9. Agentic RAG

Agentic RAG uses a controller to choose among retrieval tools or repeat retrieval based on observations. It is useful when tasks are dynamic and multi-step, but a fixed workflow is often simpler and more predictable.

~~~mermaid
flowchart TD
    Q["Question"] --> O["RAG controller"]
    O --> P["Plan evidence needs"]
    P --> T["Choose retrieval tool"]
    T --> R["Search result"]
    R --> O
    O --> D{"Enough evidence?"}
    D -->|No, budget remains| P
    D -->|Yes| G["Generate cited answer"]
    D -->|Budget exhausted| U["Explain evidence gap"]
~~~

Use an agent only when the value of dynamic decisions outweighs the added latency, complexity, and testing burden.

## 10. Worked example: evidence sufficiency

Question: "What deduction applies after an approved extension expires?"

Retrieved passage A: "Late work loses 10 percent per calendar day unless an extension has been approved."

Retrieved passage B: "The revised deadline replaces the original deadline."

These passages suggest that the revised deadline matters, but may not explicitly establish whether the deduction begins immediately after the revised deadline or how partial days are handled. A careful system should retrieve a more specific policy section or say the provided sources do not fully specify the rule.

This is an important advanced RAG skill: distinguish plausible inference from directly supported evidence.

## 11. Evaluation

Evaluate each stage independently and end to end.

| Layer | Evaluation |
|---|---|
| Routing | Correct strategy selection by query class |
| Retrieval | Recall@K, MRR, NDCG |
| Compression | Evidence-span retention and qualifier preservation |
| Multi-hop | Required-hop coverage and source linkage |
| Generation | Faithfulness, completeness, citation correctness |
| Control loop | Retry usefulness, step count, stop correctness |
| Operations | Latency, cost, failure rate |

Create test cases for contradictory sources, missing evidence, stale documents, ambiguous entities, and unauthorized content.

## 12. Python: bounded evidence-retry controller

```python
def retrieve_until_sufficient(question, retrieve, grade, max_attempts=2):
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least one")

    current_query = question
    history = []

    for attempt in range(max_attempts):
        passages = retrieve(current_query)
        assessment = grade(question, passages)
        history.append({
            "query": current_query,
            "passage_count": len(passages),
            "assessment": assessment,
        })

        if assessment["sufficient"]:
            return {
                "status": "supported",
                "passages": passages,
                "history": history,
            }

        refined = assessment.get("refined_query")
        if not refined or not refined.strip():
            break
        current_query = refined

    return {
        "status": "insufficient_evidence",
        "passages": [],
        "history": history,
    }
```

This is orchestration logic, not an implementation of a language model. The retrieve and grade functions are injected so they can be tested independently. A production version should also enforce time, cost, authorization, and maximum output limits.

## 13. Unit tests

```python
import unittest
from controller import retrieve_until_sufficient


class ControllerTests(unittest.TestCase):
    def test_stops_when_evidence_is_sufficient(self):
        def retrieve(query):
            return ["policy passage"]

        def grade(question, passages):
            return {"sufficient": True}

        result = retrieve_until_sufficient("question", retrieve, grade)
        self.assertEqual(result["status"], "supported")
        self.assertEqual(len(result["history"]), 1)

    def test_retry_is_bounded(self):
        calls = []

        def retrieve(query):
            calls.append(query)
            return []

        def grade(question, passages):
            return {"sufficient": False, "refined_query": "refined"}

        result = retrieve_until_sufficient(
            "original", retrieve, grade, max_attempts=2
        )
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(len(calls), 2)

    def test_invalid_attempt_budget(self):
        with self.assertRaises(ValueError):
            retrieve_until_sufficient("q", lambda q: [], lambda q, p: {}, 0)


if __name__ == "__main__":
    unittest.main()
```

## 14. Failure modes

| Failure | Cause | Mitigation |
|---|---|---|
| Endless retrieval loop | No hard stop condition | Attempt, time, and cost budgets |
| False evidence sufficiency | Grader overestimates support | Labelled grader evaluation and claim checks |
| Compression drops exception | Summary loses qualifiers | Preserve source spans and verify |
| Multi-hop chain drifts | Intermediate entity is wrong | Validate each hop and retain provenance |
| Graph fact is stale | Index not synchronized | Versioning and source refresh |
| Agent overuses tools | Dynamic control without cost awareness | Prefer fixed routes for simple tasks |

## 15. Interview walkthrough

**Prompt:** Design a RAG assistant for questions that often require joining information across multiple policy documents.

A strong answer:
1. Classify direct versus multi-hop questions.
2. Retrieve with hybrid search and preserve document/version metadata.
3. Decompose complex questions into explicit sub-questions.
4. Track evidence and provenance for each sub-answer.
5. Check evidence sufficiency and contradictions.
6. Use bounded retries; stop when the budget is exhausted.
7. Generate only claims supported by sources.
8. Evaluate hop coverage, retrieval quality, citations, latency, and cost.

## 16. Practice

### MCQs

1. Contextual compression aims to:
   - A. Remove source provenance
   - B. Retain relevant evidence while reducing context
   - C. Guarantee factuality
   - D. Replace retrieval

2. In multi-hop retrieval, a later query may depend on:
   - A. An intermediate result from an earlier retrieval
   - B. A random vector dimension
   - C. The final answer only
   - D. A model's confidence alone

3. Why bound corrective retrieval?
   - A. To guarantee every question is answerable
   - B. To control latency, cost, and looping
   - C. To remove citations
   - D. To avoid evaluation

### Short-answer questions

1. Explain adaptive RAG.
2. What is the risk of treating a relevance grader as a truth oracle?
3. When can a knowledge graph help RAG?
4. Why should compressed evidence retain source references?
5. When is a fixed workflow preferable to agentic RAG?

### Answer key

**MCQs:** 1-B, 2-A, 3-B.

**Short answers:**
1. It selects a retrieval strategy based on query type, complexity, or evidence needs.
2. The grader can be wrong; false positives may allow unsupported answers and false negatives may discard useful evidence.
3. When explicit entity relationships and multi-hop connections are central to the question.
4. To verify summaries, support citations, and trace claims to original content.
5. When the task is predictable and a fixed sequence is easier to test, operate, and explain.

## 17. Mini-project and completion checklist

Extend a basic RAG pipeline with a query classifier, bounded retry, evidence grading, and citation verification. Include direct, multi-hop, missing-evidence, and contradictory-source test cases.

- [ ] Explain adaptive and corrective retrieval.
- [ ] Trace a multi-hop query.
- [ ] Preserve evidence provenance during compression.
- [ ] Implement a bounded retry controller.
- [ ] Test missing and contradictory evidence.
- [ ] Compare quality, latency, and cost with basic RAG.

## Further reading

- Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*.
- Asai et al., *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*.
- Yan et al., *Corrective Retrieval Augmented Generation*.
- Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*.
