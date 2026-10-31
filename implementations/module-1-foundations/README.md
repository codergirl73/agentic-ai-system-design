# Module 1 Implementation — Minimal Tool-Using Agent

A dependency-free Python example that demonstrates the mechanics of an agent loop.

## Run

From the repository root:

```bash
python implementations/module-1-foundations/agent.py
python -m unittest discover -s implementations/module-1-foundations -p "test_*.py" -v
```

## Design

- `Tool`: a named callable with a narrow interface.
- `Planner`: deterministic decision logic for this first exercise.
- `Agent`: validates tool requests, executes tools, records events, and enforces a maximum step count.
- `AgentState`: records the goal, status, step count, and event history.

This implementation intentionally does not call an LLM. The deterministic planner makes the control flow inspectable. In a later extension, an LLM can propose structured actions, while the agent's validation, authorization, execution, and budget enforcement remain in trusted code.

## Safety and scope

The example uses a fixed allowlist of tools and validates inputs. It does not execute model-generated code, access external services, or perform consequential operations.
