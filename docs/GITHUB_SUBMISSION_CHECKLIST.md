# GitHub Repository and Submission Checklist

## Suggested repository name
`AI_Warehouse_PathPlanning_Group7`

Replace `XX` with your actual group number.

## Repository contents
- [x] Complete Python source code
- [x] `README.md` with problem statement, algorithms, dependencies and run instructions
- [x] Program output screenshots in `screenshots/`
- [x] Performance comparison table in `outputs/performance_comparison.csv`
- [x] Brief findings in this file
- [x] Names and roll numbers of all five members added to `TEAM_DETAILS.md`
- [ ] Actual GitHub repository URL
- [ ] Instructor access verified

## Brief findings
- BFS explores breadth-first and targets the fewest moves when each move is considered equal.
- DFS can find a route but is not guaranteed to return a shortest or lowest-cost route.
- Greedy Best-First prioritizes Manhattan distance and does not account for the cost already paid.
- A* combines accumulated path cost `g(n)` and heuristic `h(n)` using `f(n) = g(n) + h(n)`.
- Crowded cells cost 4, while normal cells cost 1. Therefore, a route with fewer moves can be more expensive.
- The trolley experiment demonstrates detection before entering a blocked cell, map update, and A* replanning from the robot's current position.

## Before pushing to GitHub
1. Replace `Group7` with your group number.
2. Fill in the member details in `TEAM_DETAILS.md`.
3. Review the screenshots and output files.
4. Create one GitHub repository and upload/push the complete project.
5. Give the instructor access using the repository visibility/access settings required by your course.
6. Open the repository link in a private/incognito browser or another account to check that the intended access works.

## Assignment submission email
- To: `bmakhija@iiitn.ac.in`
- Subject: `AI Group Coding Assignment Submission – Group 7`
- Include: group number, all member names and roll numbers, GitHub repository link, and group representative name and contact details.

**Deadline in the supplied assignment PDF: 18 November 2026.**


## Group 7 members
- J Lissa Jain (BT24CSD061) — Warehouse grid and search problem formulation
- Deepak Paliwal (BT24CSD040) — BFS and DFS implementation
- Kushaan Goel (BT24CSD036) — Greedy Best-First Search and heuristic explanation
- Raunak Punj (BT24CSD035) — A* implementation and weighted path costs
- Om Bawankule (BT24CSD017) — Trolley detection, map update and replanning

Still to fill: group representative contact details and the actual GitHub repository URL.
