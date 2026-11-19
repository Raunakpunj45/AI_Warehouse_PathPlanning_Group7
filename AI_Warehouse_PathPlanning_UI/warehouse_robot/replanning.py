"""
Task 4 - Trolley detection and replanning.

Two maps are used:

* TRUE map  - the real warehouse, including the trolley.
* KNOWN map - what the robot believes; the trolley is missing.

The robot plans with A* on its KNOWN map and follows the plan one cell at a
time. Before every move its sensor checks the next cell on the TRUE map. If
that cell is blocked, the robot

    1. stops BEFORE entering the blocked cell,
    2. marks the cell as a trolley on its KNOWN map,
    3. replans with A* from its CURRENT position,
    4. reports failure if no alternative route exists.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .algorithms import astar
from .grid import TROLLEY, Cell, Warehouse
from .problem import WarehouseProblem


@dataclass
class ReplanReport:
    goal_reached: bool
    executed_path: list[Cell]
    plans: list[tuple[Cell, list[Cell] | None]]       # (planned-from, plan)
    detections: list[tuple[Cell, Cell]]                # (robot position, blocked cell)
    replans: int
    total_cost: int
    nodes_expanded: int
    time_ms: float
    message: str
    log: list[str] = field(default_factory=list)
    detection_steps: list[int] = field(default_factory=list)  # index in executed_path

    @property
    def moves(self) -> int:
        return len(self.executed_path) - 1

    @property
    def original_plan(self) -> list[Cell] | None:
        return self.plans[0][1] if self.plans else None

    @property
    def final_plan(self) -> list[Cell] | None:
        return self.plans[-1][1] if self.plans else None


def run_with_replanning(true_map: Warehouse, known_map: Warehouse,
                        planner=astar, max_steps: int = 10_000) -> ReplanReport:
    known = known_map.copy(name="Robot's known map")
    pos = known.start
    executed = [pos]
    plans: list[tuple[Cell, list[Cell] | None]] = []
    detections: list[tuple[Cell, Cell]] = []
    log: list[str] = []
    detection_steps: list[int] = []
    replans = nodes = cost = 0
    t0 = time.perf_counter()

    def plan_from(cell: Cell):
        nonlocal nodes
        res = planner(WarehouseProblem(known, start=cell))
        nodes += res.nodes_expanded
        plans.append((cell, res.path))
        return res

    res = plan_from(pos)
    if not res.found:
        msg = "No route exists even on the robot's initial map."
        return ReplanReport(False, executed, plans, detections, 0, 0, nodes,
                            (time.perf_counter() - t0) * 1000, msg, [msg])

    log.append(f"Initial A* plan from {pos}: {res.moves} moves, cost {res.cost}.")
    plan, i, steps = res.path, 0, 0
    goal_reached, message = False, ""

    while steps < max_steps:
        if pos == known.goal:
            goal_reached = True
            message = f"Goal reached after {len(executed) - 1} moves with {replans} replan(s)."
            log.append(message)
            break
        nxt = plan[i + 1]
        # --- sensor: look at the next cell on the TRUE map before entering it
        if not true_map.is_passable(nxt):
            detections.append((pos, nxt))
            detection_steps.append(len(executed) - 1)
            known.place(nxt, TROLLEY)
            replans += 1
            log.append(f"Robot at {pos}: obstacle ('{true_map.symbol(nxt)}') detected at {nxt}. "
                       f"Map updated -> replanning with A* (replan #{replans}).")
            res = plan_from(pos)
            if not res.found:
                message = (f"Replanning FAILED at {pos}: no alternative route to the goal "
                           f"exists. Robot stops safely.")
                log.append(message)
                break
            log.append(f"New plan from {pos}: {res.moves} moves, cost {res.cost}.")
            plan, i = res.path, 0
            continue
        # --- safe to move
        pos = nxt
        executed.append(pos)
        cost += true_map.cost(pos)
        i += 1
        steps += 1

    return ReplanReport(goal_reached, executed, plans, detections, replans, cost, nodes,
                        (time.perf_counter() - t0) * 1000, message, log, detection_steps)


def place_trolley_on_route(warehouse: Warehouse, route: list[Cell],
                           cell: Cell | None = None) -> tuple[Warehouse, Cell]:
    """Return a TRUE map = warehouse + trolley. By default the trolley goes halfway along `route`."""
    if cell is None:
        cell = route[len(route) // 2]
    if cell not in route[1:-1]:
        raise ValueError(f"Trolley cell {cell} must lie on the route (not start/goal)")
    true_map = warehouse.copy(name=f"{warehouse.name} (true map, trolley at {cell})")
    true_map.place(cell, TROLLEY)
    return true_map, cell
