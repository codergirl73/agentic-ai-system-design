import unittest
from agent import ToolCall, ToolRuntime

class ToolRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = ToolRuntime(
            {"lookup": lambda item: f"found:{item}", "write_note": lambda text: f"saved:{text}"},
            {"lookup": {"item"}, "write_note": {"text"}},
        )

    def test_allowlisted_tool_runs(self):
        call = ToolCall("lookup", {"item": "manual"}, "k1")
        self.assertEqual(self.runtime.execute(call, "alice"), "found:manual")

    def test_unknown_tool_rejected(self):
        with self.assertRaises(PermissionError):
            self.runtime.execute(ToolCall("shell", {}, "k2"), "alice")

    def test_write_requires_approval(self):
        call = ToolCall("write_note", {"text": "hello"}, "k3")
        with self.assertRaises(PermissionError):
            self.runtime.execute(call, "alice")

    def test_idempotent_replay(self):
        call = ToolCall("lookup", {"item": "manual"}, "same")
        first = self.runtime.execute(call, "alice")
        second = self.runtime.execute(call, "alice")
        self.assertEqual(first, second)

if __name__ == "__main__":
    unittest.main()
