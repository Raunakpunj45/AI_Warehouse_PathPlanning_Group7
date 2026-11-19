"""
Warehouse layouts used in the experiments.

MAIN_WAREHOUSE
    The packing station S (left) and dispatch area G (right) are joined by a
    straight aisle that is CROWDED (C). Going straight is the shortest route in
    moves, but each crowded cell costs 4. A longer route along the open top
    aisle is cheaper - this is the "short crowded vs. longer cheaper" test.

DEAD_END_WAREHOUSE
    Only one narrow corridor leads to G. A trolley in that corridor leaves the
    robot with no alternative, so replanning must report failure.
"""

MAIN_WAREHOUSE = [
    "...............",
    ".##.####.####..",
    ".##.####.####.R",
    "S...CCCCCCC...G",
    ".##.###.#####.R",
    ".##.###.#####..",
    "...C...RRR.....",
    ".##.##.....##..",
    ".....#..C..#...",
]

DEAD_END_WAREHOUSE = [
    "S....######",
    "####.######",
    "####.RRRR##",
    "####......G",
]

# Default trolley positions (row, col) - must lie on the initial A* route.
MAIN_TROLLEY = None          # None = place it halfway along the initial A* route
DEAD_END_TROLLEY = (3, 7)
