from dataclasses import dataclass, field

@dataclass
class Session:
    goal: str
    events: list = field(default_factory=list)
    artifacts: dict = field(default_factory=dict)

def add_artifact(session, artifact_id, summary, location):
    session.artifacts[artifact_id] = {"summary": summary, "location": location}

def build_context(session, token_budget=120):
    if token_budget <= 0:
        raise ValueError("token_budget must be positive")
    header = f"Goal: {session.goal}"
    recent = session.events[-5:]
    artifact_lines = [
        f"{key}: {value['summary']} (ref: {value['location']})"
        for key, value in session.artifacts.items()
    ]
    pieces = [header] + recent + artifact_lines
    selected = []
    used = 0
    for piece in pieces:
        cost = max(1, len(piece.split()))
        if used + cost <= token_budget:
            selected.append(piece)
            used += cost
    return "\n".join(selected)
