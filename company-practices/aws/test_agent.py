import unittest
from agent import WorkflowState, run_step

class ResilienceTests(unittest.TestCase):
    def test_retries_transient_failure(self):
        state = WorkflowState()
        calls = {"n": 0}
        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise TimeoutError("temporary")
            return "ok"
        self.assertEqual(run_step(state, "lookup", flaky, 3), "ok")
        self.assertEqual(calls["n"], 3)

    def test_completed_step_is_not_repeated(self):
        state = WorkflowState(completed={"charge": "done"})
        self.assertEqual(run_step(state, "charge", lambda: "again"), "done")

    def test_non_retryable_error_propagates(self):
        with self.assertRaises(ValueError):
            run_step(WorkflowState(), "bad", lambda: (_ for _ in ()).throw(ValueError()), 3)

if __name__ == "__main__":
    unittest.main()
