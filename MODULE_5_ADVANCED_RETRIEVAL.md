# Module 5 — Advanced Retrieval: Query Understanding, Fusion and Reranking

**Level:** Intermediate → Advanced  
**Prerequisites:** Modules 2–4  
**Estimated time:** 3–4 hours  
**Build:** A multi-query retrieval pipeline with rank fusion and a reranking stage.

> This module starts after candidate retrieval. Its central question is: how can we improve the quality of the candidate set and put the most useful evidence first?

## Learning outcomes

You will learn query rewriting, decomposition, expansion, multi-query retrieval, HyDE, bi-encoders, cross-encoders, Reciprocal Rank Fusion, score calibration, candidate budgets, and evaluation by stage.

## 1. Why advanced retrieval is needed

A user may ask: "Compare the refund rules for annual and monthly plans, including exceptions."

This contains several information needs:
- annual plan refund rules;
- monthly plan refund rules;
- exceptions;
- comparison across both.

A single embedding may blur these sub-questions. Query transformation makes the intent more explicit before retrieval.

## 2. Advanced retrieval architecture

~~~mermaid
flowchart TD
    Q["Original question"] --> A["Analyze intent and constraints"]
    A --> D["Rewrite or decompose"]
    D --> Q1["Subquery 1"]
    D --> Q2["Subquery 2"]
    D --> Q3["Subquery 3"]
    Q1 --> R["Parallel retrieval"]
    Q2 --> R
    Q3 --> R
    R --> U["Deduplicate candidates"]
    U --> F["Fuse rankings"]
    F --> X["Cross-encoder reranker"]
    X --> K["Select final evidence"]
~~~

Each added stage can improve retrieval, but also adds latency, cost, and failure modes. Evaluate each stage independently.

## 3. Query rewriting

Query rewriting transforms a conversational or ambiguous question into a search-friendly query while preserving its meaning.

Example:
- Conversation: "Does that apply to the yearly option too?"
- Rewritten query: "Annual subscription refund eligibility and exceptions."

A rewrite should preserve entities, dates, negation, and constraints. A dangerous rewrite can silently change intent. Keep the original query and log the rewrite for diagnosis.

### Rewrite validation

Check:
1. Are named entities preserved?
2. Is negation preserved?
3. Are time ranges preserved?
4. Are comparison constraints preserved?
5. Does the rewrite add unsupported assumptions?

## 4. Query decomposition

Break a compound question into independent searchable sub-questions.

~~~mermaid
flowchart TD
    Q["Compare annual and monthly refund rules"] --> P["Identify information needs"]
    P --> A["Annual plan policy"]
    P --> M["Monthly plan policy"]
    P --> X["Exceptions and conditions"]
    A --> R["Retrieve evidence"]
    M --> R
    X --> R
    R --> S["Synthesize comparison"]
~~~

Decomposition is useful for multi-hop questions, comparisons, and questions requiring several sources. It is less useful for simple fact lookup. The system must retain the original question so the final synthesis answers the whole request.

## 5. Multi-query retrieval

Generate a small set of complementary queries rather than relying on one wording.

Example original question: "How do I reset access after changing phones?"

Possible queries:
- account recovery after replacing a phone;
- multi-factor authentication device migration;
- backup codes and identity verification.

Avoid generating many near-duplicates. More queries increase recall opportunities but also increase candidate noise and search cost.

## 6. HyDE: Hypothetical Document Embeddings

HyDE generates a hypothetical passage that might answer the question, then embeds that passage to retrieve similar real documents.

~~~mermaid
flowchart LR
    Q["User question"] --> H["Generate hypothetical passage"]
    H --> E["Embed hypothetical passage"]
    E --> V["Vector retrieval"]
    V --> R["Real source passages"]
    R --> C["Use retrieved evidence, not hypothetical text"]
~~~

The hypothetical text is a search aid, not evidence. It can contain fabricated details. Never cite or present the generated hypothetical passage as a source. Evaluate whether HyDE helps on your query distribution.

## 7. Bi-encoders and cross-encoders

**Bi-encoder:** encodes the query and passages independently. Passage vectors can be precomputed, making large-scale retrieval efficient.

**Cross-encoder:** processes a query and one passage together and outputs a relevance score. It can model interactions between query and passage tokens more directly, but each candidate requires inference.

~~~mermaid
flowchart TD
    Q["Query"] --> BQ["Query encoder"]
    P["Passage"] --> BP["Passage encoder"]
    BQ --> S["Vector similarity"]
    BP --> S
    S --> C["Fast candidate retrieval"]
    C --> X["Cross-encoder scores query + passage"]
    X --> R["Reranked passages"]
~~~

| Property | Bi-encoder | Cross-encoder |
|---|---|---|
| Passage vectors precomputed | Yes | No |
| Search over huge corpus | Efficient with vector index | Usually too expensive directly |
| Query-passage interaction | Separate encoding | Joint encoding |
| Typical role | Candidate generation | Reranking a smaller set |

## 8. Reranking pipeline

Retrieve perhaps 50–200 candidates, then use a reranker to score a smaller set and retain the best few. These counts are examples, not universal settings.

Measure:
- candidate Recall@N before reranking;
- NDCG@K or MRR after reranking;
- reranker latency and cost;
- quality by query category.

A reranker cannot recover a relevant passage that candidate retrieval never found.

## 9. Reciprocal Rank Fusion

RRF combines multiple ranked lists using rank positions.

\[
RRF(d)=\sum_{i=1}^{m}\frac{1}{k+rank_i(d)}
\]

If a document appears in multiple lists, it receives multiple contributions. The constant \(k\) controls how quickly rank contributions decay.

### Worked example

Let k = 60.

| Passage | Rank in lexical list | Rank in dense list |
|---|---:|---:|
| P1 | 1 | 5 |
| P2 | 3 | 1 |
| P3 | 2 | Not present |
| P4 | Not present | 2 |

Scores:
- P1 = 1/61 + 1/65 ≈ 0.0320
- P2 = 1/63 + 1/61 ≈ 0.0323
- P3 = 1/62 ≈ 0.0161
- P4 = 1/62 ≈ 0.0161

P2 ranks slightly above P1 because it ranks highly in both lists. Tie-breaking and missing-rank handling should be deterministic in implementation.

## 10. Score fusion versus rank fusion

**Score fusion** combines numeric scores, often after normalization or calibration. It can preserve score margins but requires compatible scales.

**Rank fusion** combines ordering positions. It is robust to incompatible raw score scales, but discards the size of score differences.

Choose based on data and evaluation, not preference. Always compare against single-retriever baselines.

## 11. Candidate budget and latency

A retrieval request has a latency budget. Parallel retrieval can reduce wall-clock time, but it may increase total compute. Reranking 200 candidates costs more than reranking 20.

~~~text
Original query
   |
   +-- lexical search -----------+
   |                             |
   +-- dense search -------------+--> fusion --> rerank top N --> final K
   |                             |
   +-- query variants -----------+
~~~

Trade-offs:
- More query variants may improve recall but increase cost.
- Larger candidate pools help rerankers but increase inference time.
- Stronger rerankers may improve relevance but reduce throughput.
- Caching repeated queries can reduce cost but requires freshness rules.

## 12. Python: Reciprocal Rank Fusion

```python
def reciprocal_rank_fusion(rankings, k=60):
    if k <= 0:
        raise ValueError("k must be positive")
    scores = {}
    for ranking in rankings:
        seen = set()
        for rank, item_id in enumerate(ranking, start=1):
            if item_id in seen:
                continue
            seen.add(item_id)
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))


lexical = ["P1", "P3", "P2"]
dense = ["P2", "P4", "P1"]
print(reciprocal_rank_fusion([lexical, dense]))
```

This implementation removes duplicates within each individual list, uses one-based ranks, and sorts ties by ID for deterministic output.

## 13. Unit tests

```python
import unittest
from fusion import reciprocal_rank_fusion


class RRFTests(unittest.TestCase):
    def test_item_in_two_lists_gets_two_contributions(self):
        result = dict(reciprocal_rank_fusion([["a"], ["a"]], k=60))
        self.assertAlmostEqual(result["a"], 2 / 61)

    def test_duplicate_inside_one_list_counts_once(self):
        result = dict(reciprocal_rank_fusion([["a", "a"]], k=60))
        self.assertAlmostEqual(result["a"], 1 / 61)

    def test_empty_rankings(self):
        self.assertEqual(reciprocal_rank_fusion([[], []]), [])

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([["a"]], k=0)


if __name__ == "__main__":
    unittest.main()
```

## 14. Evaluation by stage

| Stage | Evaluate | Failure question |
|---|---|---|
| Rewrite | Intent preservation | Did the query meaning change? |
| Decomposition | Sub-question coverage | Was an information need omitted? |
| Candidate retrieval | Recall@N | Did the relevant passage enter the pool? |
| Fusion | MRR / NDCG | Did useful candidates move upward? |
| Reranking | NDCG@K / MRR | Did the best evidence rise? |
| End-to-end | Answer quality, latency, cost | Did added complexity help users? |

Use ablation tests: remove one stage at a time and compare. This reveals whether the stage contributes measurable value.

## 15. Failure modes and mitigations

| Failure | Why it happens | Mitigation |
|---|---|---|
| Rewrite changes meaning | Model drops negation or constraints | Preserve original query and validate rewrite |
| Too many variants | Candidate noise and cost | Limit variants and deduplicate |
| HyDE hallucination | Hypothetical passage invents facts | Use only as retrieval signal |
| Reranker misses relevant evidence | Candidate pool has low recall | Improve first-stage recall |
| RRF favors duplicated candidates | Same passage repeated across lists | Deduplicate by stable passage ID |
| Score fusion unstable | Scores have different distributions | Calibrate or use rank fusion |
| Latency spikes | Too many sequential model calls | Parallelize safe retrieval and set budgets |

## 16. Interview walkthrough

**Prompt:** A hybrid search system finds relevant passages, but the best passage is often ranked 8th. How would you improve it?

A strong answer:
1. Inspect labelled queries and current candidate recall.
2. Determine whether the best passage is in the candidate pool.
3. If missing, improve query formulation, retrieval coverage, or index quality.
4. If present but low-ranked, test fusion and a cross-encoder reranker.
5. Compare MRR/NDCG before and after.
6. Track p50/p95 latency and compute cost.
7. Keep a held-out test set and inspect regressions.

## 17. Practice

### MCQs

1. A cross-encoder typically:
   - A. Encodes each passage once for all queries
   - B. Scores a query and passage jointly
   - C. Replaces the document index
   - D. Guarantees factual answers

2. HyDE's generated passage should be treated as:
   - A. Verified source evidence
   - B. A search representation only
   - C. A citation
   - D. A user permission

3. RRF combines rankings primarily using:
   - A. Raw cosine scores
   - B. Rank positions
   - C. Document length
   - D. Token count

### Short-answer questions

1. When is query decomposition useful?
2. Why can a reranker not fix a missing candidate?
3. Compare bi-encoders and cross-encoders.
4. Explain score fusion versus rank fusion.
5. Why preserve the original user query?

### Calculation problems

1. With k=60, an item ranks 1st in one list and 3rd in another. Calculate its RRF score.
2. A candidate retriever returns 100 items and contains 9 of 10 relevant passages. Calculate Recall@100.
3. Query reciprocal ranks are 1, 1/2, 1/4, and 0. Calculate MRR.

### Answer key

**MCQs:** 1-B, 2-B, 3-B.

**Short answers:**
1. For compound, comparison, and multi-hop questions with distinct information needs.
2. A reranker only reorders candidates it receives; it cannot score a passage that was never retrieved.
3. Bi-encoders encode independently and support efficient vector search; cross-encoders jointly process query and passage and are usually used on a smaller candidate set.
4. Score fusion combines calibrated numeric scores; rank fusion combines positions and avoids raw-score scale mismatch.
5. It allows auditing, fallback, and checking whether the rewrite preserved intent.

**Calculations:**
1. 1/61 + 1/63 ≈ 0.03226.
2. 9/10 = 0.90.
3. (1 + 0.5 + 0.25 + 0) / 4 = 0.4375.

## 18. Mini-project and completion checklist

Build a retrieval pipeline with at least two query variants, two retrievers, RRF, and a reranking interface. Compare the baseline with each added stage.

- [ ] Preserve and inspect original and rewritten queries.
- [ ] Implement query decomposition for compound questions.
- [ ] Implement RRF and unit tests.
- [ ] Measure candidate recall before reranking.
- [ ] Measure ranking quality after reranking.
- [ ] Report latency and cost for each stage.
- [ ] Demonstrate one case where added complexity does not help.

## Further reading

- Nogueira and Cho, *Passage Re-ranking with BERT*.
- Cormack, Clarke, and Buettcher, *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods*.
- Gao et al., *Precise Zero-Shot Dense Retrieval without Relevance Labels* (HyDE).
