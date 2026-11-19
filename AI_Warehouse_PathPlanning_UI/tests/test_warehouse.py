"""Unit tests - run with:  python -m unittest discover -s tests -v"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from warehouse_robot.algorithms import ALGORITHMS, astar, bfs, uniform_cost  # noqa: E402
from warehouse_robot.grid import Warehouse  # noqa: E402
from warehouse_robot.layouts import DEAD_END_TROLLEY, DEAD_END_WAREHOUSE, MAIN_WAREHOUSE  # noqa: E402
from warehouse_robot.problem import WarehouseProblem  # noqa: E402
from warehouse_robot.replanning import place_trolley_on_route, run_with_replanning  # noqa: E402


def valid_path(wh, path):
    if path[0] != wh.start or path[-1] != wh.goal:
        return False
    for a, b in zip(path, path[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1 or not wh.is_passable(b):
            return False
    return True


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.wh = Warehouse(MAIN_WAREHOUSE)

    def test_costs(self):
        self.assertEqual(self.wh.cost((3, 4)), 4)      # crowded
        self.assertEqual(self.wh.cost((0, 0)), 1)      # open

    def test_blocked_cells(self):
        self.assertFalse(self.wh.is_passable((1, 1)))  # shelf
        self.assertFalse(self.wh.is_passable((2, 14)))  # restricted
        self.assertFalse(self.wh.is_passable((-1, 0)))  # outside grid


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.wh = Warehouse(MAIN_WAREHOUSE)
        self.problem = WarehouseProblem(self.wh)

    def test_all_algorithms_return_valid_paths(self):
        for name, fn in ALGORITHMS.items():
            res = fn(self.problem)
            self.assertTrue(res.found, name)
            self.assertTrue(valid_path(self.wh, res.path), name)
            self.assertEqual(res.cost, self.wh.path_cost(res.path), name)

    def test_astar_is_cost_optimal(self):
        self.assertEqual(astar(self.problem).cost, uniform_cost(self.problem).cost)

    def test_bfs_has_fewest_moves(self):
        b = bfs(self.problem).moves
        for fn in ALGORITHMS.values():
            self.assertLessEqual(b, fn(self.problem).moves)

    def test_shortest_is_not_cheapest(self):
        b, a = bfs(self.problem), astar(self.problem)
        self.assertLess(b.moves, a.moves)
        self.assertGreater(b.cost, a.cost)

    def test_heuristic_is_admissible(self):
        for r in range(self.wh.rows):
            for c in range(self.wh.cols):
                if self.wh.is_passable((r, c)):
                    p = WarehouseProblem(self.wh, start=(r, c))
                    true_cost = uniform_cost(p).cost
                    if true_cost is not None:
                        self.assertLessEqual(p.heuristic((r, c)), true_cost)

    def test_no_route(self):
        wh = Warehouse(["S#G"])
        for fn in ALGORITHMS.values():
            self.assertFalse(fn(WarehouseProblem(wh)).found)


class TestReplanning(unittest.TestCase):
    def test_replan_success(self):
        wh = Warehouse(MAIN_WAREHOUSE)
        plan = astar(WarehouseProblem(wh)).path
        true_map, trolley = place_trolley_on_route(wh, plan)
        rep = run_with_replanning(true_map, wh)
        self.assertTrue(rep.goal_reached)
        self.assertEqual(rep.replans, 1)
        self.assertNotIn(trolley, rep.executed_path)
        self.assertTrue(valid_path(true_map, rep.executed_path))

    def test_replan_failure(self):
        wh = Warehouse(DEAD_END_WAREHOUSE)
        plan = astar(WarehouseProblem(wh)).path
        true_map, _ = place_trolley_on_route(wh, plan, DEAD_END_TROLLEY)
        rep = run_with_replanning(true_map, wh)
        self.assertFalse(rep.goal_reached)
        self.assertIn("no alternative", rep.message.lower())


if __name__ == "__main__":
    unittest.main()
