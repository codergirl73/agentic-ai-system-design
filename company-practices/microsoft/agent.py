from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    allowed_users: frozenset

def retrieve_for_user(user_id, query, documents):
    query_terms = set(query.lower().split())
    visible = []
    audit = []
    for doc in documents:
        allowed = user_id in doc.allowed_users
        audit.append({"doc_id": doc.doc_id, "user": user_id, "allowed": allowed})
        if allowed and query_terms.intersection(doc.text.lower().split()):
            visible.append(doc)
    return visible, audit
