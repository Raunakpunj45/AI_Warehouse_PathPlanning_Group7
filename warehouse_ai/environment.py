"""Member 1: Warehouse grid and search problem formulation."""
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

Position = Tuple[int, int]

@dataclass
class Warehouse:
    rows: int = 12
    cols: int = 16
    start: Position = (1, 1)
    goal: Position = (10, 14)

    def __post_init__(self):
        # Cells are (row, column). Shelves and restricted zones are impassable.
        self.shelves: Set[Position] = {
            (r, c) for r in range(2, 10) for c in (4, 11)
        } | {(5, c) for c in range(6, 10)}
        self.restricted: Set[Position] = {
            (r, c) for r in range(7, 10) for c in range(7, 10)
        }
        self.crowded: Set[Position] = {
            (1, c) for c in range(5, 10)
        } | {(r, 8) for r in range(2, 6)} | {
            (8, c) for c in range(11, 14)
        }
        # Ensure special cells do not overlap impassable cells or endpoints.
        self.crowded -= self.shelves | self.restricted | {self.start, self.goal}
        self.shelves.discard(self.start)
        self.shelves.discard(self.goal)
        self.restricted.discard(self.start)
        self.restricted.discard(self.goal)

    def in_bounds(self, p: Position) -> bool:
        return 0 <= p[0] < self.rows and 0 <= p[1] < self.cols

    def is_blocked(self, p: Position, extra_blocked: Optional[Set[Position]] = None) -> bool:
        extra_blocked = extra_blocked or set()
        return p in self.shelves or p in self.restricted or p in extra_blocked

    def passable(self, p: Position, extra_blocked: Optional[Set[Position]] = None) -> bool:
        return self.in_bounds(p) and not self.is_blocked(p, extra_blocked)

    def neighbors(self, p: Position, extra_blocked: Optional[Set[Position]] = None) -> List[Position]:
        # Fixed order makes demonstrations reproducible: up, down, left, right.
        r, c = p
        candidates = [(r-1,c), (r+1,c), (r,c-1), (r,c+1)]
        return [q for q in candidates if self.passable(q, extra_blocked)]

    def step_cost(self, p: Position) -> int:
        """Cost of entering p: crowded=4, every other traversable cell=1."""
        return 4 if p in self.crowded else 1

    def path_cost(self, path: List[Position]) -> int:
        return sum(self.step_cost(p) for p in path[1:])

    def manhattan(self, p: Position) -> int:
        return abs(p[0] - self.goal[0]) + abs(p[1] - self.goal[1])

    def display(self, path=None, extra_blocked=None, title="Warehouse"):
        path = set(path or [])
        extra_blocked = extra_blocked or set()
        print(f"\n{title}  (S=start, G=goal, #=shelf, X=restricted, ~=crowded, *=route, T=trolley)")
        print("   " + " ".join(f"{c:2}" for c in range(self.cols)))
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                p = (r, c)
                if p == self.start: ch = "S"
                elif p == self.goal: ch = "G"
                elif p in extra_blocked: ch = "T"
                elif p in self.restricted: ch = "X"
                elif p in self.shelves: ch = "#"
                elif p in path: ch = "*"
                elif p in self.crowded: ch = "~"
                else: ch = "."
                row.append(f"{ch:>2}")
            print(f"{r:2} " + " ".join(row))

    # Problem formulation required by Task 2.
    def problem_formulation(self) -> Dict[str, str]:
        return {
            "State": "The robot's current grid coordinate (row, column).",
            "Initial state": f"{self.start}",
            "Actions": "Move one cell Up, Down, Left, or Right.",
            "Transition model": "Move to an in-bounds, non-blocked adjacent cell.",
            "Goal test": f"Current coordinate equals {self.goal}.",
            "Path-cost function": "Sum of costs of entered cells: normal=1, crowded=4."
        }
