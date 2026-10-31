import unittest

from agent import Agent, Tool, build_agent, calculator


class AgentTests(unittest.TestCase):
    def test_calculator_add(self):
        self.assertEqual(calculator("add", 2, 3), 5)

    def test_calculator_multiply(self):
        self.assertEqual(calculator("multiply", 4, 5), 20)

    def test_unknown_calculator_operation_fails(self):
        with self.assertRaises(ValueError):
            calculator("divide", 4, 2)

    def test_agent_completes_multiply_goal(self):
        result = build_agent().run("Multiply two numbers")
        self.assertEqual(result.status, "completed")
        self.assertIn("50", result.final_answer)

    def test_agent_searches_demo_index(self):
        result = build_agent().run("Search: Graph RAG")
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(result.events[0]["result"]), 2)

    def test_unknown_goal_returns_explanation(self):
        result = build_agent().run("Explain agent memory")
        self.assertEqual(result.status, "completed")
        self.assertIn("could not map", result.final_answer)

    def test_unknown_tool_is_rejected(self):
        agent = build_agent()
        with self.assertRaises(Exception):
            agent._validate_and_execute({"tool": "shell", "arguments": {"cmd": "echo unsafe"}})

    def test_max_steps_must_be_positive(self):
        with self.assertRaises(ValueError):
            Agent(tools={}, max_steps=0)


if __name__ == "__main__":
    unittest.main()
