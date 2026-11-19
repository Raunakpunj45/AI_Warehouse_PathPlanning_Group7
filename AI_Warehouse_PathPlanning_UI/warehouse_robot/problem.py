"""
Task 2 - Problem formulation.

    State            : the robot's position (row, col) on the grid.
    Initial state    : the packing station S (or the robot's current cell when replanning).
    Actions(s)       : the subset of {Up, Down, Left, Right} whose target cell is inside
                       the grid and is not a shelf, restricted zone or known trolley.
    Transition model : Result(s, a) = s + delta(a), where
                       Up=(-1,0), Down=(+1,0), Left=(0,-1), Right=(0,+1).
    Goal test        : s == G (the dispatch area).
    Path cost        : sum of step costs; step cost c(s, a, s') = cost of ENTERING s'
                       = 1 for an open cell, 4 for a crowded cell.
    Heuristic h(s)   : Manhattan distance |r - r_G| + |c - c_G|  (used by Greedy and A*).
"""

from __future__ import annotations

from .grid import MOVES, Cell, Warehouse


class WarehouseProblem:
    """Search problem defined on a (possibly partially known) warehouse map."""

    def __init__(self, warehouse: Warehouse, start: Cell | None = None):
        self.warehouse = warehouse
        self.initial_state: Cell = start if start is not None else warehouse.start
        self.goal: Cell = warehouse.goal

    def actions(self, state: Cell) -> list[str]:
        return [action for action, _ in self.warehouse.neighbors(state)]

    def result(self, state: Cell, action: str) -> Cell:
        dr, dc = MOVES[action]
        return (state[0] + dr, state[1] + dc)

    def goal_test(self, state: Cell) -> bool:
        return state == self.goal

    def step_cost(self, state: Cell, action: str, next_state: Cell) -> int:
        return self.warehouse.cost(next_state)

    def successors(self, state: Cell):
        """Yield (action, next_state, step_cost) for every legal action."""
        for action, nxt in self.warehouse.neighbors(state):
            yield action, nxt, self.warehouse.cost(nxt)

    def heuristic(self, state: Cell) -> int:
        """Manhattan distance to the goal - admissible and consistent here (see README)."""
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])
