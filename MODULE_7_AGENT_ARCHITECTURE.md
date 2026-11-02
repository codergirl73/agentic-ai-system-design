# Module 7 — Agent Architecture and Orchestration

**Level:** Intermediate → Advanced  
**Prerequisites:** Module 1 and the retrieval modules  
**Estimated time:** 4–5 hours  
**Build:** A bounded, stateful agent workflow with typed tools, validation, checkpoints, and approval gates.

## Learning outcomes

Explain tool calling, planning, state and memory, orchestration patterns, state machines, single-agent and multi-agent architectures, delegation, human approval, and evaluation. Choose the simplest architecture that meets the task requirements.

## 1. What orchestration solves

A model can suggest a next action, but an application must decide whether that action is valid, permitted, affordable, and useful. Orchestration coordinates model calls, tools, state updates, retries, and stopping conditions.

Example task: research a topic, compare sources, and prepare a report. The system may need search, document reading, note-taking, and synthesis. The orchestrator tracks which steps are complete and which evidence supports each conclusion.

## 2. Reference architecture

~~~mermaid
flowchart TD
    U["User task"] --> I["Input and policy checks"]
    I --> O["Orchestrator"]
    O --> M["Model proposes next step"]
    M --> V["Validate tool and arguments"]
    V -->|Allowed| G["Tool gateway"]
    V -->|Not allowed| H["Ask, reject, or stop"]
    G --> T["Approved tools"]
    T --> R["Tool result"]
    R --> S["Update task state"]
    S --> O
    O --> E["Evaluate completion"]
    E -->|Done| F["Final response"]
    E -->|More work| M
~~~

The model proposes; the application validates and executes. Keep this separation explicit.

## 3. Tool calling and schemas

A tool is a named capability with a defined input and output contract. For example:

```python
def search_papers(query: str, limit: int = 5) -> list[dict]:
    """Search approved paper metadata and return candidate records."""
    if not query.strip():
        raise ValueError("query must not be empty")
    if not 1 <= limit <= 10:
        raise ValueError("limit must be between 1 and 10")
    return []
```

A schema should define:
- tool name and purpose;
- required and optional arguments;
- types, bounds, and allowed values;
- output structure;
- errors and timeout behavior;
- permission and side-effect classification.

Validate at the boundary even if the model was asked to produce valid arguments. Model output is untrusted input.

## 4. Planning and task decomposition

Planning converts a goal into subgoals, dependencies, and completion checks.

~~~mermaid
flowchart TD
    G["Research and compare three papers"] --> P["Create plan"]
    P --> A["Find candidate papers"]
    P --> B["Read and extract methods"]
    P --> C["Compare evidence"]
    A --> D["Check three valid sources"]
    B --> D
    D --> E["Synthesize cited report"]
~~~

A useful plan is executable and observable. Each step should have an expected output, dependency, and failure behavior. Avoid plans with vague steps such as "think more."

## 5. State versus memory

**Task state** is the structured information required to continue the current run. **Memory** is information retained beyond the run for later use.

| Data | Example | Typical lifetime |
|---|---|---|
| Current subtask | Read paper 2 | One run |
| Completed source IDs | Paper A, Paper B | One run |
| Retry count | 1 of 3 | One run |
| User-approved preference | Preferred report format | Across runs, if saved appropriately |
| Long-term knowledge | Indexed research documents | Managed storage lifecycle |

Do not put all historical data into every model prompt. Store structured state separately and retrieve only the relevant context.

## 6. State-machine orchestration

~~~mermaid
stateDiagram-v2
    [*] --> Validate
    Validate --> Plan
    Plan --> SelectAction
    SelectAction --> Execute: allowed
    SelectAction --> Approval: approval needed
    SelectAction --> Stop: invalid or budget exhausted
    Execute --> Observe
    Observe --> UpdateState
    UpdateState --> Evaluate
    Evaluate --> Plan: more work
    Evaluate --> Finish: goal satisfied
    Approval --> Execute: approved
    Approval --> Stop: declined or expired
    Finish --> [*]
    Stop --> [*]
~~~

A state machine makes allowed transitions explicit. It is easier to test than a free-form loop with implicit state.

## 7. Stop conditions and budgets

Use explicit limits:
- maximum model and tool steps;
- wall-clock deadline;
- token or monetary budget;
- maximum retries per tool;
- no-progress detection;
- cancellation and approval timeout.

A system should return a partial result and explain what remains when a budget is exhausted. Never claim completion just because the loop ended.

## 8. Single-agent patterns

A single agent is often enough when one controller can manage the task and tools.

Common patterns:
- ReAct-style reasoning and acting;
- plan-then-execute;
- router that selects a specialist tool;
- evaluator/critic pass;
- retrieval-augmented agent.

A fixed workflow may be better than an agent when the sequence is stable. Dynamic decisions are useful only when they add measurable value.

## 9. Multi-agent patterns

~~~mermaid
flowchart TD
    U["User goal"] --> S["Supervisor"]
    S --> R["Research worker"]
    S --> A["Analysis worker"]
    S --> W["Writing worker"]
    R --> X["Shared task state"]
    A --> X
    W --> X
    X --> S
    S --> V["Validate and synthesize"]
    V --> F["Final result"]
~~~

Possible patterns include supervisor-worker, peer collaboration, sequential handoff, and parallel specialists.

Multi-agent systems add coordination overhead:
- more model calls and latency;
- shared-state consistency problems;
- duplicated work;
- harder debugging;
- broader permission surface;
- error propagation between agents.

Use separate agents when tasks can be decomposed into genuinely distinct responsibilities and parallelism or specialization justifies the cost. Do not create agents merely to make a diagram look sophisticated.

## 10. Shared state and concurrency

If two workers update the same task record, define ownership and conflict behavior. Options include:
- one writer per field;
- append-only event logs;
- version numbers and compare-and-swap;
- transactional updates;
- immutable worker outputs merged by a supervisor.

Never assume parallel workers finish in the order they were started.

## 11. Human-in-the-loop approval

Use approval for actions that are consequential, difficult to reverse, externally visible, or outside pre-authorized bounds.

~~~mermaid
flowchart TD
    A["Proposed action"] --> V["Validate arguments and scope"]
    V --> C{"Consequential action?"}
    C -->|No| E["Execute within policy"]
    C -->|Yes| H["Present action and impact for approval"]
    H --> D{"Approved?"}
    D -->|Yes| E
    D -->|No| S["Cancel and record decision"]
    E --> R["Verify outcome"]
~~~

Approval should show the exact action, target, data to be changed, and likely impact. A generic "approve?" prompt is not enough.

## 12. Python: bounded orchestration loop

```python
def run_agent(goal, decide, tools, max_steps=5):
    if max_steps < 1:
        raise ValueError("max_steps must be positive")

    state = {"goal": goal, "observations": [], "status": "running"}

    for step in range(max_steps):
        proposal = decide(state)

        if proposal["action"] == "finish":
            state["status"] = "complete"
            state["final"] = proposal.get("answer", "")
            return state

        tool_name = proposal.get("tool")
        arguments = proposal.get("arguments", {})
        if tool_name not in tools:
            state["status"] = "stopped_invalid_tool"
            return state

        try:
            result = tools[tool_name](**arguments)
        except (TypeError, ValueError) as exc:
            state["observations"].append({"error": str(exc)})
            continue

        state["observations"].append({
            "tool": tool_name,
            "result": result,
        })

    state["status"] = "step_budget_exhausted"
    return state
```

This teaching loop is deliberately small. A production orchestrator needs typed schemas, authorization, timeouts, cancellation, idempotency, trace IDs, structured errors, and careful handling of untrusted tool results.

## 13. Unit tests

```python
import unittest
from agent_loop import run_agent


class AgentLoopTests(unittest.TestCase):
    def test_executes_allowed_tool_then_finishes(self):
        decisions = iter([
            {"action": "call", "tool": "lookup", "arguments": {"key": "x"}},
            {"action": "finish", "answer": "Found it"},
        ])
        result = run_agent(
            "find x", lambda state: next(decisions),
            {"lookup": lambda key: "value"},
        )
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["final"], "Found it")

    def test_rejects_unknown_tool(self):
        result = run_agent(
            "goal", lambda state: {
                "action": "call", "tool": "unknown", "arguments": {}
            }, {}
        )
        self.assertEqual(result["status"], "stopped_invalid_tool")

    def test_stops_at_step_budget(self):
        result = run_agent(
            "goal", lambda state: {
                "action": "call", "tool": "ping", "arguments": {}
            }, {"ping": lambda: "ok"}, max_steps=2
        )
        self.assertEqual(result["status"], "step_budget_exhausted")

    def test_invalid_budget(self):
        with self.assertRaises(ValueError):
            run_agent("goal", lambda state: {}, {}, max_steps=0)


if __name__ == "__main__":
    unittest.main()
```

## 14. Evaluation and observability

Measure:
- task success against a defined rubric;
- tool-call validity and success rate;
- steps per task and no-progress loops;
- approval frequency and rejection rate;
- latency and cost;
- recovery after tool errors;
- quality of final evidence and citations.

Trace each step with a run ID, state transition, tool name, validated arguments (redacted where needed), duration, result status, and budget remaining. Do not log secrets or unnecessary personal data.

## 15. Failure modes

| Failure | Cause | Mitigation |
|---|---|---|
| Tool called with invalid arguments | Model output not validated | Schema validation at executor boundary |
| Repeated same action | No-progress loop | Detect repeated state/action pairs |
| Worker overwrites another | Shared-state race | Ownership, versioning, or append-only events |
| Agent stops too early | Weak completion test | Explicit goal acceptance criteria |
| Agent never stops | No hard budget | Step, time, and cost caps |
| Approval unclear | User cannot inspect impact | Show exact action and consequences |

## 16. Interview walkthrough

**Prompt:** Design a research assistant that can search papers, compare findings, and create a report.

1. Clarify sources, freshness, expected number of papers, output, latency, and budget.
2. Start with one orchestrator and read-only tools.
3. Define a typed task state and source provenance.
4. Add a plan with verifiable milestones.
5. Validate tool calls and enforce bounded execution.
6. Use parallel workers only if independent paper analysis justifies the coordination cost.
7. Add evidence checks and a final synthesis stage.
8. Trace each step and evaluate task success, cost, and failure recovery.

## 17. Practice

### MCQs

1. The orchestrator should:
   - A. Execute every model proposal without validation
   - B. Coordinate state, tools, policies, and stopping
   - C. Store all data in the prompt
   - D. Guarantee the model is correct

2. Task state primarily describes:
   - A. Current run progress
   - B. Every past conversation
   - C. Model training weights
   - D. External search ranking only

3. Multi-agent architecture is most justified when:
   - A. More agents look impressive
   - B. Distinct responsibilities or parallelism provide measurable value
   - C. One tool call is sufficient
   - D. Shared state is unnecessary

### Short-answer questions

1. Explain why tool arguments must be validated even if generated from a schema.
2. Distinguish task state from long-term memory.
3. Name four stop conditions.
4. Give two costs of multi-agent systems.
5. When should human approval be required?

### Answer key

**MCQs:** 1-B, 2-A, 3-B.

**Short answers:**
1. Model output is untrusted and may be malformed, incomplete, or outside allowed bounds.
2. State tracks the current run; memory retains selected information across runs.
3. Step, time, cost, retry, no-progress, or cancellation limits.
4. More calls and latency, shared-state conflicts, harder debugging, duplicated work, and wider permissions.
5. For consequential, irreversible, externally visible, or insufficiently pre-authorized actions.

## 18. Mini-project and completion checklist

Build a stateful research workflow with two read-only tools, explicit state, a step budget, structured traces, and tests for invalid tool requests and failures. Add an approval checkpoint in a simulated consequential action.

- [ ] Define tool schemas and validate arguments.
- [ ] Implement a bounded state machine.
- [ ] Track task state separately from memory.
- [ ] Test invalid tool names and malformed arguments.
- [ ] Explain when multi-agent design is justified.
- [ ] Add traces and a measurable completion rubric.

## Further reading

- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*.
- Schick et al., *Toolformer: Language Models Can Teach Themselves to Use Tools*.
- Wu et al., *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*.
