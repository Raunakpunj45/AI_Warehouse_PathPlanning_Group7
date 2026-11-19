## Algorithm comparison

| Algorithm | Goal reached | Path length (moves) | Total path cost | Nodes expanded | Execution time (ms) |
|---|---|---|---|---|---|
| BFS | Yes | 14 | 35 | 64 | 0.103 |
| DFS | Yes | 32 | 38 | 72 | 0.134 |
| Greedy Best-First | Yes | 14 | 35 | 15 | 0.032 |
| A* | Yes | 20 | 20 | 31 | 0.070 |

## Trolley / replanning experiments

| Scenario | Goal reached | Path length (moves) | Total path cost | Nodes expanded | Execution time (ms) | Replans |
|---|---|---|---|---|---|---|
| A: trolley on A* route | Yes | 34 | 37 | 70 | 0.216 | 1 |
| B: dead-end corridor | No | 9 | 9 | 24 | 0.083 | 1 |

## Shortest vs. cheapest

NO - the shortest route was NOT the cheapest. BFS found the fewest moves (14 moves) but it crosses crowded cells, so it costs 35. A* took 20 moves (6 more) but its cost is only 20 (15 less), because it avoids the crowded aisle.
