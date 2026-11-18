# AI-Based Route Planning for a Warehouse Delivery Robot

A complete Python implementation of the five tasks in the supplied AI Group Coding Assignment.

## Requirements
- Python 3.9 or newer
- No third-party packages required for the core program

## Run the integrated project
Open a terminal in this folder and run:

```bash
python main.py
```

The complete console demonstration is also saved to `outputs/run_output.txt`.

## Run each member's module separately
```bash
python member1_environment.py
python member2_bfs_dfs.py
python member3_greedy.py
python member4_astar.py
python member5_replanning.py
```

Each member module imports the shared implementation in `warehouse_ai/`. The integrated `main.py` runs all tasks together.

## Assignment coverage
1. **Warehouse environment:** grid, start, goal, shelves, restricted zones, crowded cells, four-direction movement.
2. **Problem formulation:** state, initial state, actions, transition model, goal test and path-cost function.
3. **Search:** BFS, DFS, Greedy Best-First and A* on the same grid.
4. **Dynamic obstacle:** a trolley is absent from the initial map, detected before entry, added to the known blocked cells, and A* replans from the robot's current position.
5. **Evaluation:** goal reached, moves, weighted cost, nodes expanded and execution time; trolley experiment records replans.

## Grid legend
- `S`: start
- `G`: goal
- `.`: normal traversable cell (entry cost 1)
- `~`: crowded cell (entry cost 4)
- `#`: shelf (blocked)
- `X`: restricted zone (blocked)
- `T`: detected trolley (blocked)
- `*`: route

Coordinates are `(row, column)`, starting at zero. The robot can move up, down, left or right.

## Algorithm notes
- **BFS:** finds a route with the fewest moves when every move is treated equally. It does not optimize the assignment's weighted cost.
- **DFS:** explores deeply according to neighbor ordering; it is not guaranteed to return a shortest or cheapest route.
- **Greedy Best-First:** prioritizes Manhattan distance `h(n)` only; it is not guaranteed to find the cheapest route.
- **A\*:** prioritizes `f(n) = g(n) + h(n)`, where `g(n)` is the cost already paid and `h(n)` is Manhattan distance to the goal.

### Why Manhattan distance is admissible here
A legal action changes either the row or column by one. Therefore at least
`|row - goal_row| + |column - goal_column|` moves are required. Every entered
traversable cell costs at least 1, while crowded cells cost 4. Manhattan distance
therefore cannot exceed the true remaining weighted cost; it is an admissible
lower bound.

## Important interpretation
BFS and DFS are included as required comparison algorithms. Because crowded cells
have a higher cost, the fewest-move path may not be the lowest-cost path. A* is the
algorithm used for weighted-cost route planning and replanning.

## Project structure
```text
AI_Warehouse_Route_Planning/
├── main.py
├── member1_environment.py
├── member2_bfs_dfs.py
├── member3_greedy.py
├── member4_astar.py
├── member5_replanning.py
├── warehouse_ai/
│   ├── environment.py
│   ├── search.py
│   ├── replanning.py
│   └── evaluation.py
├── outputs/
├── docs/
│   ├── MEMBER_WORK_EXPLANATION.md
│   └── PROJECT_REPORT.md
└── requirements.txt
```

## GitHub submission checklist
- Create one repository for the group.
- Upload the complete project folder.
- Add all five students' names and roll numbers to the member document.
- Add screenshots of a successful full run and trolley replanning.
- Give the instructor repository access.
- Submit one group email as instructed in the assignment PDF.

## Limitations / extension
The environment is a deterministic simulation. The trolley is a single newly
discovered static obstacle. The optional GUI/animation is not required for the
core assignment and can be added later.


## Submission evidence
- Output screenshots: `screenshots/`
- Captured full console output: `outputs/run_output.txt`
- Performance table (CSV): `outputs/performance_comparison.csv`
- GitHub submission checklist: `docs/GITHUB_SUBMISSION_CHECKLIST.md`
- Team names and contributions: `docs/TEAM_DETAILS.md`
- Submission email template: `docs/SUBMISSION_EMAIL_TEMPLATE.txt`
- References acknowledgement: `docs/REFERENCES_AND_ACKNOWLEDGEMENT.md`

Before submission, fill all team placeholders and paste the actual GitHub repository URL.


## Group 7
**Repository name:** `AI_Warehouse_PathPlanning_Group7`

| Member | Roll number | Contribution |
|---|---|---|
| J Lissa Jain | BT24CSD061 | Warehouse grid and problem formulation |
| Deepak Paliwal | BT24CSD040 | BFS and DFS |
| Kushaan Goel | BT24CSD036 | Greedy Best-First Search and heuristic |
| Raunak Punj | BT24CSD035 | A* and weighted path costs |
| Om Bawankule | BT24CSD017 | Trolley detection and replanning |

See `docs/TEAM_DETAILS.md` for the contribution record. Add the final repository URL and representative contact details before emailing the instructor.
