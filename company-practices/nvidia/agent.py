from dataclasses import dataclass
from collections import defaultdict

@dataclass(frozen=True)
class Request:
    request_id: str
    model: str
    payload: str

def make_batches(requests, max_batch_size):
    if max_batch_size < 1:
        raise ValueError("max_batch_size must be positive")
    groups = defaultdict(list)
    for request in requests:
        groups[request.model].append(request)
    batches = []
    for model in sorted(groups):
        items = groups[model]
        for start in range(0, len(items), max_batch_size):
            batches.append((model, items[start:start + max_batch_size]))
    return batches
