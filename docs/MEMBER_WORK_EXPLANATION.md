# Group 7 — Five-Member Work Division and Viva Explanation

**Project:** AI-Based Route Planning for a Warehouse Delivery Robot

| Member | Name | Roll number | Assigned responsibility |
|---|---|---|---|
| 1 | J Lissa Jain | BT24CSD061 | Warehouse grid and search problem formulation |
| 2 | Deepak Paliwal | BT24CSD040 | BFS and DFS implementation |
| 3 | Kushaan Goel | BT24CSD036 | Greedy Best-First Search and heuristic explanation |
| 4 | Raunak Punj | BT24CSD035 | A* implementation and weighted path costs |
| 5 | Om Bawankule | BT24CSD017 | Trolley detection, map update and replanning |

## Member 1 — J Lissa Jain (BT24CSD061)
**Responsibility:** Warehouse grid and search problem formulation.

Explain the 2D grid, start and goal coordinates, normal/crowded/blocked cells, four legal actions, transition model, goal test and path-cost function.

## Member 2 — Deepak Paliwal (BT24CSD040)
**Responsibility:** BFS and DFS implementation.

Explain queue-based breadth-first exploration, stack-based depth-first exploration, visited/parent tracking, path reconstruction, and why BFS minimizes moves but not necessarily weighted cost.

## Member 3 — Kushaan Goel (BT24CSD036)
**Responsibility:** Greedy Best-First Search and heuristic explanation.

Explain the Manhattan heuristic, priority queue, why Greedy chooses states based on estimated distance only, and why it is not guaranteed to return the least-cost path.

## Member 4 — Raunak Punj (BT24CSD035)
**Responsibility:** A* implementation and weighted path costs.

Explain g(n), h(n), f(n)=g(n)+h(n), crowded-cell cost 4, normal-cell cost 1, and why Manhattan distance is admissible for this four-direction grid.

## Member 5 — Om Bawankule (BT24CSD017)
**Responsibility:** Trolley detection, map update and replanning.

Explain the initially hidden trolley, detection before entering the blocked cell, updating the known blocked cells, replanning from the robot's current position using A*, and reporting success/failure.

## Shared evaluation expectation
Every member should understand the overall pipeline:
1. Build the warehouse and define the search problem.
2. Run BFS, DFS, Greedy Best-First and A* on the same grid.
3. Compare moves, weighted path cost, nodes expanded and execution time.
4. Detect the previously unknown trolley.
5. Update the map and replan with A*.
6. Explain why fewest moves and lowest weighted cost can differ.
