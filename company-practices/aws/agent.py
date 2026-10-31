from dataclasses import dataclass, field

@dataclass
class WorkflowState:
    completed: dict = field(default_factory=dict)
    attempts: dict = field(default_factory=dict)

def run_step(state, step_id, operation, max_attempts=3, retryable=(TimeoutError,)):
    if step_id in state.completed:
        return state.completed[step_id]
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    for attempt in range(1, max_attempts + 1):
        state.attempts[step_id] = attempt
        try:
            result = operation()
            state.completed[step_id] = result
            return result
        except retryable:
            if attempt == max_attempts:
                raise
    raise RuntimeError("unreachable")
