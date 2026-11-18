# Project Report
## AI-Based Route Planning for a Warehouse Delivery Robot

### 1. Introduction
A warehouse delivery robot must move packages from a packing station to a dispatch area. Shelves and restricted zones make some cells impassable, crowded aisles increase travel cost, and a trolley may unexpectedly block a route. This project models the warehouse as a 2D grid and compares four AI search algorithms.

### 2. Objectives
- Model a warehouse with normal, crowded and blocked cells.
- Formulate route planning as a search problem.
- Implement BFS, DFS, Greedy Best-First Search and A*.
- Simulate discovery of a previously unknown trolley.
- Update the robot's known map and replan with A*.
- Compare search performance.

### 3. Environment and assumptions
The warehouse is a finite rectangular grid. A state is a `(row, column)` coordinate. The robot can move one cell up, down, left or right. Normal cells cost 1 to enter and crowded cells cost 4. Shelves, restricted zones and a detected trolley are impassable. The environment is deterministic.

### 4. Problem formulation
- **State space:** all traversable grid coordinates.
- **Initial state:** `(1, 1)`.
- **Actions:** up, down, left, right.
- **Transition model:** move to an adjacent in-bounds traversable cell.
- **Goal state:** `(10, 14)`.
- **Path cost:** sum of costs of all entered cells; start-cell cost is not charged.

### 5. Algorithms
**BFS:** FIFO queue, explores by depth and returns a minimum-move route in an unweighted graph.

**DFS:** LIFO stack, explores a branch deeply before backtracking. It does not guarantee shortest or minimum-cost paths.

**Greedy Best-First Search:** selects the frontier state with the smallest Manhattan heuristic. It may reach the goal quickly but does not account for the cost already paid.

**A*:** uses `f(n) = g(n) + h(n)`. Here `g(n)` is the accumulated weighted cost and `h(n)` is Manhattan distance to the goal.

### 6. Heuristic admissibility
For a four-direction grid, each action changes one coordinate by one. Thus at least `|row - goal_row| + |column - goal_column|` actions remain. Each entered traversable cell costs at least 1. Therefore Manhattan distance is no greater than the true remaining weighted cost and is admissible.

### 7. Weighted-route experiment
The integrated program also runs a small controlled grid where the direct route
crosses crowded cells (entry cost 4), while a detour uses more moves through
normal cells (entry cost 1). BFS illustrates the fewest-move route and A*
illustrates the minimum-cost route. The exact measured moves and costs are
printed by `python main.py` and saved in `outputs/run_output.txt`.

### 8. Dynamic obstacle handling
The initial A* plan is generated without the trolley in the robot's known map. The trolley is placed on a cell of the planned route. Before the robot enters that cell, it detects the trolley, marks the cell as blocked, and invokes A* from its current position to the destination. The output records the number of replans and whether a new route exists.

### 9. Performance evaluation
The program measures:
- Whether the goal was reached.
- Number of moves in the returned path.
- Total weighted path cost.
- Number of nodes expanded.
- Execution time in milliseconds.
- Number of replans in the trolley experiment.

Run `python main.py` to generate the actual comparison table for the current environment. Timing varies by computer and execution conditions; do not copy timing values from another machine.

### 10. Expected discussion
The shortest route by number of moves is not necessarily the least-cost route because crowded cells cost four times as much as normal cells. BFS optimizes number of moves when steps are treated equally. A* incorporates weighted path cost and an admissible lower-bound heuristic. DFS and Greedy are not guaranteed to produce a minimum-cost route.

### 11. Conclusion
The project demonstrates classical uninformed and informed search algorithms in a warehouse navigation problem. It also demonstrates a simple dynamic replanning cycle: detect an unknown obstacle, update the map, and compute a replacement route. A* is suitable for the weighted environment because it considers both cost already incurred and an admissible estimate of the remaining cost.

### 12. Team contributions
Insert the five members' names, roll numbers and individual contributions from `MEMBER_WORK_EXPLANATION.md`.

### 13. References
- Artificial Intelligence — Group Coding Assignment, “AI-Based Route Planning for a Warehouse Delivery Robot,” supplied course handout.
- Any additional external references used by the group should be acknowledged here.


## Group 7 contributions

# Group 7 — Team Details and Contributions

**Project:** AI-Based Route Planning for a Warehouse Delivery Robot  
**Repository name:** `AI_Warehouse_PathPlanning_Group7`  
**Group number:** 7

| Member | Full name | Roll number | Contribution |
|---|---|---|---|
| 1 | J Lissa Jain | BT24CSD061 | Warehouse grid and search problem formulation |
| 2 | Deepak Paliwal | BT24CSD040 | BFS and DFS implementation |
| 3 | Kushaan Goel | BT24CSD036 | Greedy Best-First Search and heuristic explanation |
| 4 | Raunak Punj | BT24CSD035 | A* implementation and weighted path costs |
| 5 | Om Bawankule | BT24CSD017 | Trolley detection, map update and replanning |

**Group representative:** [Confirm representative]  
**Representative contact:** [Add email address / phone number]  
**GitHub repository URL:** [Paste repository URL after creating it]

All five members should be prepared to explain the overall system as well as their assigned module.
