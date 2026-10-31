"""A small, dependency-free tool-using agent for Module 1.

This is a teaching implementation. The planner is deterministic rather than
LLM-powered so that the control loop and trust boundaries are easy to inspect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]


@dataclass
class AgentState:
    goal: str
    status: str = "running"
    steps: int = 0
    events: list[dict[str, Any]] = field(default_factory=list)
    final_answer: str | None = None


class ToolError(Exception):
    """Raised when a tool request is invalid or cannot be executed."""


def calculator(operation: str, a: float, b: float) -> float:
    """Perform a supported arithmetic operation."""
    if operation == "add":
        return a + b
    if operation == "multiply":
        return a * b
    raise ValueError(f"Unsupported operation: {operation}")


def search_demo(query: str) -> list[dict[str, str]]:
    """Return deterministic mock search results; no network access is used."""
    if not query.strip():
        raise ValueError("query must not be empty")
    return [
        {
            "title": f"Introductory result about {query}",
            "source": "demo://research-index/1",
        },
        {
            "title": f"Further reading about {query}",
            "source": "demo://research-index/2",
        },
    ]


class SimplePlanner:
    """A deliberately simple planner that emits one structured action."""

    def plan(self, goal: str) -> dict[str, Any]:
        normalized = goal.lower()
        if "multiply" in normalized:
            return {
                "tool": "calculator",
                "arguments": {"operation": "multiply", "a": 10, "b": 5},
            }
        if "add" in normalized:
            return {
                "tool": "calculator",
                "arguments": {"operation": "add", "a": 10, "b": 5},
            }
        if "search" in normalized:
            query = goal.split(":", 1)[1].strip() if ":" in goal else goal
            return {"tool": "search", "arguments": {"query": query}}
        return {"final": "I could not map this goal to an available demo action."}


class Agent:
    def __init__(
        self,
        tools: dict[str, Tool],
        planner: SimplePlanner | None = None,
        max_steps: int = 3,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1")
        self.tools = tools
        self.planner = planner or SimplePlanner()
        self.max_steps = max_steps

    def _validate_and_execute(self, action: dict[str, Any]) -> Any:
        tool_name = action.get("tool")
        arguments = action.get("arguments", {})

        # Allowlist check: never execute arbitrary names or generated code.
        if tool_name not in self.tools:
            raise ToolError(f"Tool is not allowed: {tool_name}")
        if not isinstance(arguments, dict):
            raise ToolError("Tool arguments must be a dictionary")

        # Validate each tool's expected argument names and basic types.
        if tool_name == "calculator":
            required = {"operation", "a", "b"}
            if set(arguments) != required:
                raise ToolError(f"calculator expects exactly: {sorted(required)}")
            if arguments["operation"] not in {"add", "multiply"}:
                raise ToolError("Unsupported calculator operation")
            if not isinstance(arguments["a"], (int, float)):
                raise ToolError("a must be numeric")
            if not isinstance(arguments["b"], (int, float)):
                raise ToolError("b must be numeric")
        elif tool_name == "search":
            if set(arguments) != {"query"}:
                raise ToolError("search expects exactly one argument: query")
            if not isinstance(arguments["query"], str) or not arguments["query"].strip():
                raise ToolError("query must be a non-empty string")

        return self.tools[tool_name].function(**arguments)

    def run(self, goal: str) -> AgentState:
        state = AgentState(goal=goal)

        while state.steps < self.max_steps:
            action = self.planner.plan(state.goal)
            state.steps += 1

            if "final" in action:
                state.status = "completed"
                state.final_answer = action["final"]
                state.events.append({"step": state.steps, "type": "final"})
                return state

            try:
                result = self._validate_and_execute(action)
                state.events.append(
                    {
                        "step": state.steps,
                        "type": "tool_result",
                        "tool": action["tool"],
                        "result": result,
                    }
                )
                state.status = "completed"
                state.final_answer = f"Task completed. Result: {result}"
                return state
            except (ToolError, ValueError, TypeError) as exc:
                state.events.append(
                    {
                        "step": state.steps,
                        "type": "tool_error",
                        "error": str(exc),
                    }
                )
                state.status = "failed"
                state.final_answer = f"Task could not be completed: {exc}"
                return state

        state.status = "max_steps_reached"
        state.final_answer = "Stopped safely: maximum step budget reached."
        return state


def build_agent(max_steps: int = 3) -> Agent:
    tools = {
        "calculator": Tool(
            name="calculator",
            description="Add or multiply two numbers.",
            function=calculator,
        ),
        "search": Tool(
            name="search",
            description="Search a small local demonstration index.",
            function=search_demo,
        ),
    }
    return Agent(tools=tools, max_steps=max_steps)


if __name__ == "__main__":
    agent = build_agent()
    for sample_goal in (
        "Multiply two numbers",
        "Add two numbers",
        "Search: Graph RAG",
        "Explain agent memory",
    ):
        result = agent.run(sample_goal)
        print(f"Goal: {result.goal}")
        print(f"Status: {result.status}")
        print(f"Answer: {result.final_answer}")
        print(f"Events: {result.events}")
        print("-" * 60)
