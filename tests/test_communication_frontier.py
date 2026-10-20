import unittest

from src.communication_frontier import first_hit, running_min


class CommunicationFrontierTests(unittest.TestCase):
    def test_first_hit_uses_exact_cumulative_bytes_field(self):
        history = [
            {"round": 1, "val_mae": 20.0, "cumulative_bytes": 12345},
            {"round": 2, "val_mae": 15.0, "cumulative_bytes": 54321},
            {"round": 3, "val_mae": 14.0, "cumulative_bytes": 99999},
        ]
        hit = first_hit(history, target=15.0)
        self.assertIsNotNone(hit)
        self.assertEqual(hit["round"], 2)
        self.assertEqual(hit["cumulative_bytes"], 54321)
        self.assertNotEqual(hit["cumulative_bytes"], 0)

    def test_first_hit_is_first_recorded_hit_not_best_checkpoint(self):
        history = [
            {"round": 1, "val_mae": 11.0, "cumulative_bytes": 100},
            {"round": 2, "val_mae": 9.0, "cumulative_bytes": 200},
            {"round": 3, "val_mae": 8.0, "cumulative_bytes": 300},
        ]
        hit = first_hit(history, target=10.0)
        self.assertEqual((hit["round"], hit["cumulative_bytes"]), (2, 200))

    def test_unreached_target_returns_none_for_explicit_censoring(self):
        history = [
            {"round": 1, "val_mae": 20.0, "cumulative_bytes": 615600},
            {"round": 2, "val_mae": 19.0, "cumulative_bytes": 1231200},
        ]
        self.assertIsNone(first_hit(history, target=18.999))

    def test_running_minimum_is_monotone_and_retains_bytes(self):
        history = [
            {"round": 1, "val_mae": 10.0, "cumulative_bytes": 11},
            {"round": 2, "val_mae": 12.0, "cumulative_bytes": 22},
            {"round": 3, "val_mae": 9.0, "cumulative_bytes": 33},
        ]
        points = running_min(history)
        self.assertEqual(points, [(11, 1, 10.0), (22, 2, 10.0), (33, 3, 9.0)])
        self.assertEqual([point[2] for point in points], sorted((point[2] for point in points), reverse=True))


if __name__ == "__main__":
    unittest.main()
