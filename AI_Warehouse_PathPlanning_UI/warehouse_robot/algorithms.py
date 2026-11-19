"""
Task 3 - Search algorithms: BFS, DFS, Greedy Best-First Search and A*.

All four are graph searches (they never re-expand a state) and share the same
conventions so that their numbers are comparable:

* Successors are generated in the order Up, Down, Left, Right.
* The goal test is applied when a node is taken OUT of the frontier.
* "Nodes expanded" = number of states taken out of the frontier and processed
  (the goal state, when reached, is counted too).
"""

from __future__ import annotations

import heapq
import itertools
import time
from collections import deque
from dataclasses import dataclass, field

from .grid import Cell
from .problem import WarehouseProblem


@dataclass
class SearchResult:
    algorithm: str
    path: list[Cell] | None
    cost: int | None
    nodes_expanded: int
    time_ms: float = 0.0
    explored_order: list[Cell] = field(default_factory=list, repr=False)

    @property
    def found(self) -> bool:
        return self.path is not None

    @property
    def moves(self) -> int | None:
        return len(self.path) - 1 if self.path else None


def _reconstruct(parent: dict[Cell, Cell | None], goal: Cell) -> list[Cell]:
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def _finish(name, problem, parent, goal_node, expanded, order):
    if goal_node is None:
        return SearchResult(name, None, None, expanded, explored_order=order)
    path = _reconstruct(parent, goal_node)
    return SearchResult(name, path, problem.warehouse.path_cost(path), expanded,
                        explored_order=order)


# --------------------------------------------------------------------------- BFS
def bfs(problem: WarehouseProblem) -> SearchResult:
    """Breadth-First Search: FIFO frontier -> fewest moves, ignores cell costs."""
    start = problem.initial_state
    frontier = deque([start])
    parent: dict[Cell, Cell | None] = {start: None}
    expanded, order = 0, []
    while frontier:
        node = frontier.popleft()
        expanded += 1
        order.append(node)
        if problem.goal_test(node):
            return _finish("BFS", problem, parent, node, expanded, order)
        for _, nxt, _ in problem.successors(node):
            if nxt not in parent:          # not yet reached
                parent[nxt] = node
                frontier.append(nxt)
    return _finish("BFS", problem, parent, None, expanded, order)


# --------------------------------------------------------------------------- DFS
def dfs(problem: WarehouseProblem) -> SearchResult:
    """Depth-First Search: LIFO frontier -> finds *a* path, usually not short or cheap."""
    start = problem.initial_state
    stack = [start]
    parent: dict[Cell, Cell | None] = {start: None}
    visited: set[Cell] = set()
    expanded, order = 0, []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        expanded += 1
        order.append(node)
        if problem.goal_test(node):
            return _finish("DFS", problem, parent, node, expanded, order)
        # push in reverse so that "Up" is explored first
        for _, nxt, _ in reversed(list(problem.successors(node))):
            if nxt not in visited:
                parent[nxt] = node
                stack.append(nxt)
    return _finish("DFS", problem, parent, None, expanded, order)


# ------------------------------------------------------------ Greedy Best-First
def greedy_best_first(problem: WarehouseProblem) -> SearchResult:
    """Greedy Best-First: expands the node with the smallest h(n) (Manhattan distance)."""
    start = problem.initial_state
    tie = itertools.count()
    frontier = [(problem.heuristic(start), next(tie), start)]
    parent: dict[Cell, Cell | None] = {start: None}
    visited: set[Cell] = set()
    expanded, order = 0, []
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in visited:
            continue
        visited.add(node)
        expanded += 1
        order.append(node)
        if problem.goal_test(node):
            return _finish("Greedy Best-First", problem, parent, node, expanded, order)
        for _, nxt, _ in problem.successors(node):
            if nxt not in visited and nxt not in parent:
                parent[nxt] = node
                heapq.heappush(frontier, (problem.heuristic(nxt), next(tie), nxt))
    return _finish("Greedy Best-First", problem, parent, None, expanded, order)


# ---------------------------------------------------------------------------- A*
def astar(problem: WarehouseProblem) -> SearchResult:
    """A*: expands the node with the smallest f(n) = g(n) + h(n). Optimal in path cost."""
    start = problem.initial_state
    tie = itertools.count()
    g: dict[Cell, int] = {start: 0}
    parent: dict[Cell, Cell | None] = {start: None}
    frontier = [(problem.heuristic(start), problem.heuristic(start), next(tie), start)]
    closed: set[Cell] = set()
    expanded, order = 0, []
    while frontier:
        _, _, _, node = heapq.heappop(frontier)
        if node in closed:                 # stale queue entry
            continue
        closed.add(node)
        expanded += 1
        order.append(node)
        if problem.goal_test(node):
            return _finish("A*", problem, parent, node, expanded, order)
        for _, nxt, step in problem.successors(node):
            new_g = g[node] + step
            if nxt not in closed and new_g < g.get(nxt, float("inf")):
                g[nxt] = new_g
                parent[nxt] = node
                h = problem.heuristic(nxt)
                heapq.heappush(frontier, (new_g + h, h, next(tie), nxt))
    return _finish("A*", problem, parent, None, expanded, order)


# ------------------------------------------------------------ uniform-cost check
def uniform_cost(problem: WarehouseProblem) -> SearchResult:
    """Dijkstra / UCS - used only by the tests to verify that A* is cost-optimal."""
    class _Zero(WarehouseProblem):
        def heuristic(self, state):
            return 0
    zero = _Zero(problem.warehouse, problem.initial_state)
    res = astar(zero)
    res.algorithm = "UCS"
    return res


ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "Greedy Best-First": greedy_best_first,
    "A*": astar,
}


def timed(search_fn, problem: WarehouseProblem, repeats: int = 30) -> SearchResult:
    """Run a search `repeats` times and store the average wall-clock time in ms."""
    result = search_fn(problem)
    t0 = time.perf_counter()
    for _ in range(repeats):
        search_fn(problem)
    result.time_ms = (time.perf_counter() - t0) * 1000 / repeats
    return result
