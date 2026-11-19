"""
Task 1 - Warehouse environment.

The warehouse is a 2D grid. Every cell holds one character:

    .   open aisle        (cost to enter = 1)
    C   crowded aisle     (cost to enter = 4)
    #   shelf             (impassable)
    R   restricted zone   (impassable)
    S   start  - packing station  (behaves like an open cell)
    G   goal   - dispatch area    (behaves like an open cell)
    T   trolley           (impassable; only in the TRUE map, see replanning.py)

Positions are (row, col) tuples; row 0 is the top row.
"""

from __future__ import annotations

OPEN = "."
CROWDED = "C"
SHELF = "#"
RESTRICTED = "R"
START = "S"
GOAL = "G"
TROLLEY = "T"

BLOCKED = {SHELF, RESTRICTED, TROLLEY}
STEP_COST = {OPEN: 1, START: 1, GOAL: 1, CROWDED: 4}

# Allowed moves, in the fixed order used by every algorithm.
MOVES = {
    "Up": (-1, 0),
    "Down": (1, 0),
    "Left": (0, -1),
    "Right": (0, 1),
}

Cell = tuple[int, int]


class Warehouse:
    """A rectangular warehouse grid built from a list of equal-length strings."""

    def __init__(self, layout: list[str], name: str = "Warehouse"):
        if not layout or any(len(row) != len(layout[0]) for row in layout):
            raise ValueError("Layout must be a non-empty list of equal-length strings")
        self.name = name
        self.grid = [list(row) for row in layout]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.start = self._find(START)
        self.goal = self._find(GOAL)

    # ------------------------------------------------------------------ helpers
    def _find(self, symbol: str) -> Cell:
        hits = [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.grid[r][c] == symbol]
        if len(hits) != 1:
            raise ValueError(f"Layout must contain exactly one '{symbol}', found {len(hits)}")
        return hits[0]

    def symbol(self, cell: Cell) -> str:
        r, c = cell
        return self.grid[r][c]

    def in_bounds(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_passable(self, cell: Cell) -> bool:
        return self.in_bounds(cell) and self.symbol(cell) not in BLOCKED

    def cost(self, cell: Cell) -> int:
        """Cost of ENTERING `cell` (1 for normal cells, 4 for crowded cells)."""
        return STEP_COST[self.symbol(cell)]

    def neighbors(self, cell: Cell) -> list[tuple[str, Cell]]:
        """Legal (action, next_cell) pairs from `cell`, in Up/Down/Left/Right order."""
        r, c = cell
        out = []
        for action, (dr, dc) in MOVES.items():
            nxt = (r + dr, c + dc)
            if self.is_passable(nxt):
                out.append((action, nxt))
        return out

    def path_cost(self, path: list[Cell]) -> int:
        return sum(self.cost(cell) for cell in path[1:])

    # --------------------------------------------------------------- mutation
    def copy(self, name: str | None = None) -> "Warehouse":
        return Warehouse(["".join(row) for row in self.grid], name or self.name)

    def place(self, cell: Cell, symbol: str) -> None:
        if cell in (self.start, self.goal):
            raise ValueError("Cannot place an obstacle on the start or goal cell")
        r, c = cell
        self.grid[r][c] = symbol

    # -------------------------------------------------------------- rendering
    def render(self, path: list[Cell] | None = None, marks: dict[Cell, str] | None = None) -> str:
        """ASCII picture of the grid. Path cells are shown as '*' (or 'o' on crowded cells)."""
        on_path = set(path or [])
        marks = marks or {}
        header = "     " + " ".join(f"{c % 10}" for c in range(self.cols))
        lines = [header, "    +" + "-" * (2 * self.cols) + "+"]
        for r in range(self.rows):
            cells = []
            for c in range(self.cols):
                cell = (r, c)
                ch = self.grid[r][c]
                if cell in marks:
                    ch = marks[cell]
                elif cell in on_path and ch not in (START, GOAL):
                    ch = "o" if ch == CROWDED else "*"
                cells.append(ch)
            lines.append(f" {r:2d} |" + " ".join(cells) + " |")
        lines.append("    +" + "-" * (2 * self.cols) + "+")
        return "\n".join(lines)


LEGEND = ("Legend: S=start  G=goal  .=open(1)  C=crowded(4)  #=shelf  R=restricted  "
          "T=trolley  *=route  o=route through crowded cell  X=robot")
