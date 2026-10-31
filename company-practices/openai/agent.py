from dataclasses import dataclass

@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict
    idempotency_key: str

class ToolRuntime:
    def __init__(self, tools, required_fields, approved=()):
        self.tools = tools
        self.required_fields = required_fields
        self.approved = set(approved)
        self.completed = {}

    def execute(self, call: ToolCall, actor: str):
        if call.name not in self.tools:
            raise PermissionError("Tool is not allowlisted")
        missing = set(self.required_fields[call.name]) - set(call.arguments)
        if missing:
            raise ValueError(f"Missing fields: {sorted(missing)}")
        if call.name.startswith("write_") and call.idempotency_key not in self.approved:
            raise PermissionError("Human approval required")
        key = (actor, call.idempotency_key)
        if key in self.completed:
            return self.completed[key]
        result = self.tools[call.name](**call.arguments)
        self.completed[key] = result
        return result
