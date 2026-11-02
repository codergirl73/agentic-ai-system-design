# Module 4 — Information Retrieval

**Level:** Intermediate → Advanced  
**Prerequisites:** Modules 2 and 3  
**Estimated time:** 3–4 hours  
**Build:** A small retrieval benchmark comparing lexical, dense, and hybrid search.

> Learning sequence: understand the search problem → build an index → retrieve candidates → rank results → evaluate → tune trade-offs.

## Learning outcomes

By the end, you should be able to explain how search engines represent documents, build lexical and dense retrieval baselines, calculate ranking metrics, combine candidate lists, diagnose retrieval failures, and design a retrieval service.

## 1. The retrieval problem

A knowledge base may contain thousands or millions of passages. Given a query, retrieval finds a small set of candidates likely to contain useful evidence.

Example query: **"What happens if I submit an assignment late?"**

Relevant passage: "Late work loses 10 percent per calendar day unless an extension has been approved."

A useful retriever must bridge wording differences, identify the right passage, and return it quickly. Retrieval is not answer generation: it selects evidence for a later stage.

## 2. Search architecture

~~~mermaid
flowchart TD
    Q["User query"] --> N["Normalize and analyze query"]
    N --> L["Lexical retriever"]
    N --> D["Dense retriever"]
    L --> LC["Lexical candidates"]
    D --> DC["Vector candidates"]
    LC --> F["Candidate fusion"]
    DC --> F
    F --> R["Ranked results"]
    R --> K["Top K passages"]
    K --> E["Evaluation and diagnostics"]
~~~

**Component responsibilities**

| Component | Responsibility | Typical design question |
|---|---|---|
| Analyzer | Tokenize, normalize, handle language | Which terms should remain distinct? |
| Inverted index | Map terms to documents | How much index memory is acceptable? |
| Lexical retriever | Match terms and score candidates | BM25 or a field-aware variant? |
| Vector index | Find nearby embeddings | Exact or approximate nearest neighbors? |
| Fusion | Combine retrieval channels | Rank fusion or score calibration? |
| Evaluator | Measure retrieval quality | Which queries and relevance labels? |

## 3. Lexical retrieval and inverted indexes

A simple search engine builds an inverted index: each term points to the documents or passages containing it.

~~~text
Passage P1: "late assignment penalty"
Passage P2: "approved assignment extension"
Passage P3: "library opening hours"

Inverted index (simplified)
assignment -> P1, P2
late       -> P1
penalty    -> P1
extension  -> P2
library    -> P3
~~~

This representation avoids scanning every passage for every query. A real index also stores term frequencies, document lengths, positions, and other statistics.

### Tokenization and normalization

Tokenization turns text into terms. Normalization may lowercase words, normalize Unicode, remove selected punctuation, or apply language-specific processing. Stemming and lemmatization reduce word variants, but can damage names, codes, and domain-specific terms. Keep exact identifiers searchable.

### BM25 intuition

BM25 scores a passage using query-term frequency, term rarity across the collection, and document length normalization. Rare query terms are often more informative than common terms. Repeating a term helps, but the benefit saturates.

A common form is:

\[
\operatorname{BM25}(q,d)=\sum_{t\in q} IDF(t)\cdot
\frac{f(t,d)(k_1+1)}{f(t,d)+k_1(1-b+b\frac{|d|}{avgdl})}
\]

Where:
- \(f(t,d)\): frequency of term \(t\) in document \(d\)
- \(|d|\): document length
- \(avgdl\): average document length
- \(k_1,b\): tuning parameters
- \(IDF(t)\): inverse document-frequency weight

Do not memorize the formula without understanding the behavior: rare terms matter more, repeated terms have diminishing returns, and length normalization prevents long passages from winning simply because they contain more words.

## 4. Dense retrieval

Dense retrieval encodes a query and each passage into vectors. A nearest-neighbor search finds passages whose vectors are close to the query vector.

~~~mermaid
flowchart LR
    Q["Question"] --> QE["Query encoder"]
    P["Passages"] --> PE["Passage encoder"]
    QE --> VQ["Query vector"]
    PE --> VP["Passage vectors"]
    VQ --> S["Similarity search"]
    VP --> S
    S --> R["Nearest passages"]
~~~

The query and passage encoders must produce compatible vectors. Some models use the same encoder; others use separate query and document instructions or encoders. Follow the model's intended usage.

Dense search can match paraphrases, but it may struggle with rare product IDs, exact legal clauses, names, dates, or newly introduced vocabulary. Lexical search is often valuable for those cases.

## 5. Exact versus approximate nearest-neighbor search

For a small collection, exact search can compare the query vector against every stored vector. Cost grows with the number of vectors and dimensions.

For large collections, approximate nearest-neighbor (ANN) indexes reduce search work by exploring only promising regions or graph neighbors. Examples of index families include graph-based and inverted-file approaches.

| Choice | Advantage | Cost / risk |
|---|---|---|
| Exact scan | Simple and exact | Query cost grows with corpus size |
| ANN | Lower latency at scale | May miss some true nearest neighbors |
| Higher search effort | Often improves recall | More CPU, memory, and latency |

The correct choice depends on corpus size, update rate, latency target, hardware, and acceptable recall loss. Benchmark with your own queries.

## 6. Hybrid retrieval

Hybrid retrieval combines lexical and dense candidate lists.

~~~mermaid
flowchart TD
    Q["Query"] --> B["BM25 search"]
    Q --> V["Dense search"]
    B --> C["Candidate union"]
    V --> C
    C --> F["Rank fusion"]
    F --> R["Final ranked passages"]
~~~

A practical starting point is to retrieve a larger candidate pool from each channel and combine ranks with Reciprocal Rank Fusion (RRF).

\[
RRF(d)=\sum_{r\in rankings}\frac{1}{k+rank_r(d)}
\]

RRF uses rank positions rather than raw scores, which avoids directly adding uncalibrated BM25 and cosine scores. It does not know which retriever is more trustworthy; evaluation is still required.

## 7. Worked example: Precision@K and Recall@K

Suppose the gold relevant passages for a query are {P1, P3, P5}. The system returns [P3, P2, P1, P8].

At K=4:
- Relevant retrieved = 2 (P3 and P1)
- Precision@4 = 2/4 = **0.50**
- Recall@4 = 2/3 = **0.667**

Precision asks: "How many returned passages were relevant?"  
Recall asks: "How many of the relevant passages did we find?"

For multiple queries, calculate each query's metric and report an appropriate aggregate, often the mean.

## 8. Ranking metrics

### Mean Reciprocal Rank (MRR)

If the first relevant result appears at rank 3, reciprocal rank is 1/3. MRR averages reciprocal rank across queries. It rewards systems that place at least one useful result near the top.

### Normalized Discounted Cumulative Gain (NDCG)

NDCG supports graded relevance. A highly relevant passage should contribute more than a partially relevant passage, and high-ranked results receive more weight. It is useful when relevance is not simply binary.

Metrics answer different questions. Report more than one and inspect examples; an aggregate can hide important failure cases.

## 9. Build a retrieval evaluation set

Create a small labelled dataset before tuning:
1. Write realistic user questions.
2. Identify relevant passage IDs for each query.
3. Use a consistent relevance scale, such as 0 = irrelevant, 1 = related, 2 = useful, 3 = directly answers.
4. Split queries into development and held-out test sets.
5. Compare BM25, dense, and hybrid retrieval on the same queries.
6. Inspect failures, not only average scores.

Avoid using the test set repeatedly to tune parameters; that leaks evaluation feedback into the design.

## 10. Python baseline: metric calculations

```python
def precision_at_k(retrieved, relevant, k):
    if k <= 0:
        raise ValueError("k must be positive")
    top_k = retrieved[:k]
    return sum(item in relevant for item in top_k) / len(top_k) if top_k else 0.0


def recall_at_k(retrieved, relevant, k):
    if k <= 0:
        raise ValueError("k must be positive")
    if not relevant:
        return 0.0
    return sum(item in relevant for item in retrieved[:k]) / len(relevant)


def reciprocal_rank(retrieved, relevant):
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


gold = {"P1", "P3", "P5"}
results = ["P3", "P2", "P1", "P8"]
print(precision_at_k(results, gold, 4))  # 0.5
print(recall_at_k(results, gold, 4))     # 0.666...
print(reciprocal_rank(results, gold))   # 1.0
```

## 11. Tests

```python
import unittest
from retrieval_metrics import precision_at_k, recall_at_k, reciprocal_rank


class RetrievalMetricTests(unittest.TestCase):
    def test_precision_and_recall(self):
        gold = {"a", "c", "e"}
        ranked = ["c", "b", "a", "d"]
        self.assertEqual(precision_at_k(ranked, gold, 4), 0.5)
        self.assertAlmostEqual(recall_at_k(ranked, gold, 4), 2 / 3)

    def test_reciprocal_rank(self):
        self.assertEqual(reciprocal_rank(["x", "c", "a"], {"a", "c"}), 0.5)

    def test_no_relevant_result(self):
        self.assertEqual(reciprocal_rank(["x", "y"], {"a"}), 0.0)

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            precision_at_k(["a"], {"a"}, 0)


if __name__ == "__main__":
    unittest.main()
```

Save the first code block as `retrieval_metrics.py` and the second as `test_retrieval_metrics.py`, then run `python -m unittest -v`.

## 12. Failure analysis

| Symptom | Possible cause | Diagnostic |
|---|---|---|
| Exact IDs are missed | Analyzer altered identifiers | Test punctuation and case variants |
| Paraphrases are missed | Weak dense model or query mismatch | Inspect query and passage vectors |
| Relevant passage ranks low | Fusion or scoring issue | Compare channel-specific ranks |
| Results are noisy | Query too broad or weak filters | Inspect candidate pool |
| ANN misses gold results | Search effort too low | Compare against exact search |
| Offline metric looks good, users unhappy | Dataset mismatch | Collect real anonymized query patterns |

## 13. System-design trade-offs

| Decision | Optimize for | Trade-off |
|---|---|---|
| BM25 only | Exact terms and simplicity | Weaker paraphrase matching |
| Dense only | Semantic matching | May miss rare exact terms |
| Hybrid | Coverage across query types | More components and tuning |
| Larger candidate pool | Recall | More reranking and latency |
| ANN | Scale and latency | Approximation error |
| More metadata filters | Precision and permissions | Filter selectivity and index complexity |

Always apply authorization constraints before returning passages. A high relevance score never overrides access permissions.

## 14. Interview walkthrough

**Prompt:** Design search for a knowledge base with two million technical passages. Users ask natural-language questions but also search exact error codes.

A strong answer:
1. Clarify query mix, corpus updates, languages, access control, latency, and relevance targets.
2. Preserve exact identifiers with lexical search.
3. Add dense retrieval for semantic paraphrases.
4. Fuse candidates, then optionally rerank.
5. Enforce tenant and document permissions in retrieval.
6. Evaluate Recall@K, MRR/NDCG, latency, and cost.
7. Benchmark ANN recall against exact search on a representative sample.
8. Monitor query categories and retrieval failures.

## 15. Practice

### MCQs

1. An inverted index maps:
   - A. Documents to embedding dimensions
   - B. Terms to documents containing them
   - C. Queries to model weights
   - D. Users to permissions

2. Which metric measures the fraction of relevant items found in the top K relative to all known relevant items?
   - A. Precision@K
   - B. Recall@K
   - C. MRR
   - D. Latency

3. Why can hybrid retrieval help?
   - A. It removes the need for evaluation
   - B. It combines lexical exact matching and semantic matching
   - C. It guarantees correct answers
   - D. It eliminates indexing

### Short-answer questions

1. Explain the purpose of an inverted index.
2. Explain one difference between BM25 and dense retrieval.
3. Why should BM25 and cosine similarity scores not automatically be added?
4. What does MRR reward?
5. Why compare ANN with exact search?

### Calculation problems

1. Gold relevant IDs are {A, C, E, G}; results at K=5 are [C, B, A, D, H]. Calculate Precision@5 and Recall@5.
2. The first relevant results for three queries occur at ranks 1, 2, and 4. Calculate MRR.
3. A search service returns 20 results, 12 relevant. There are 30 relevant items in the corpus. Calculate precision and recall.

### Answer key

**MCQs:** 1-B, 2-B, 3-B.

**Short answers:**
1. It maps terms to the documents or passages containing them, enabling efficient term-based search.
2. BM25 uses term statistics and exact lexical overlap; dense retrieval compares learned vector representations.
3. The score scales and meanings differ. Use calibration or rank fusion such as RRF.
4. It rewards retrieving the first relevant result at a high rank.
5. It quantifies recall loss from approximation and helps tune latency/quality.

**Calculations:**
1. Relevant in top five = 2. Precision = 2/5 = 0.40; recall = 2/4 = 0.50.
2. MRR = (1 + 1/2 + 1/4) / 3 = 0.5833.
3. Precision = 12/20 = 0.60; recall = 12/30 = 0.40.

## 16. Mini-project and completion checklist

Build a benchmark over at least 30 passages and 15 labelled queries. Compare lexical, dense, and hybrid retrieval. Report Precision@5, Recall@5, MRR, median latency, and failure examples.

- [ ] Explain inverted indexes and BM25.
- [ ] Explain dense retrieval and ANN.
- [ ] Implement Precision@K, Recall@K, and MRR.
- [ ] Compare at least two retrieval approaches.
- [ ] Inspect at least five failure cases.
- [ ] Explain authorization and latency trade-offs.

## Further reading

- Robertson and Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*.
- BEIR: a heterogeneous benchmark for information retrieval.
- Malkov and Yashunin, *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs*.
