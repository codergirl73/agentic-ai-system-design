import unittest
from agent import Request, make_batches

class BatchTests(unittest.TestCase):
    def test_respects_batch_limit(self):
        requests = [Request(str(i), "m1", "x") for i in range(5)]
        batches = make_batches(requests, 2)
        self.assertEqual([len(batch) for _, batch in batches], [2, 2, 1])

    def test_never_mixes_models(self):
        requests = [Request("1", "m1", "x"), Request("2", "m2", "y")]
        batches = make_batches(requests, 8)
        self.assertEqual({model for model, _ in batches}, {"m1", "m2"})

    def test_invalid_batch_size(self):
        with self.assertRaises(ValueError):
            make_batches([], 0)

if __name__ == "__main__":
    unittest.main()
