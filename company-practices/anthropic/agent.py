from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

@dataclass(frozen=True)
class Finding:
    question: str
    claim: str
    source_url: str

def run_research(subquestions, researcher, max_workers=3):
    if max_workers < 1:
        raise ValueError("max_workers must be positive")
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(researcher, q) for q in subquestions]
        for future in as_completed(futures):
            finding = future.result()
            if not finding.source_url.startswith(("https://", "http://")):
                raise ValueError("Finding must include an HTTP(S) source")
            results.append(finding)
    return sorted(results, key=lambda item: item.question)

def conflicting_claims(findings):
    claims = {}
    for item in findings:
        claims.setdefault(item.question, set()).add(item.claim)
    return {q: sorted(values) for q, values in claims.items() if len(values) > 1}
