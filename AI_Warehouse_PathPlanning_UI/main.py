"""
AI-Based Route Planning for a Warehouse Delivery Robot
======================================================

Runs every part of the assignment and saves all figures/tables to ./outputs

    python main.py                  # run everything, save outputs
    python main.py --show           # also open the figures in windows
    python main.py --no-animation   # skip the GIF animations (faster)
    python main.py --trolley 0 9    # put the trolley at row 0, col 9 (must be on the A* route)
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


class Tee(io.TextIOBase):
    """Write console output to the screen and to a log file at the same time."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def banner(text: str) -> None:
    print("\n" + "=" * 78)
    print(f"  {text}")
    print("=" * 78)


def parse_args():
    p = argparse.ArgumentParser(description="Warehouse robot route planning (BFS, DFS, Greedy, A*)")
    p.add_argument("--show", action="store_true", help="open figure windows as well as saving them")
    p.add_argument("--no-animation", action="store_true", help="skip GIF animations")
    p.add_argument("--trolley", nargs=2, type=int, metavar=("ROW", "COL"),
                   help="trolley cell for the main experiment (default: halfway along A* route)")
    p.add_argument("--repeats", type=int, default=30,
                   help="runs averaged for execution time (default 30)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        import matplotlib
        if not args.show:
            matplotlib.use("Agg")   # save figures without opening windows
    except Exception:               # noqa: BLE001 - handled below when importing visualize
        pass

    from warehouse_robot.algorithms import astar
    from warehouse_robot.evaluate import (ALGO_HEADERS, REPLAN_HEADERS, algorithm_rows,
                                          compare_algorithms, format_table, markdown_table,
                                          replan_rows, save_csv, shortest_vs_cheapest)
    from warehouse_robot.grid import LEGEND, Warehouse
    from warehouse_robot.layouts import (DEAD_END_TROLLEY, DEAD_END_WAREHOUSE,
                                         MAIN_WAREHOUSE)
    from warehouse_robot.problem import WarehouseProblem
    from warehouse_robot.replanning import place_trolley_on_route, run_with_replanning

    OUT.mkdir(exist_ok=True)
    log_file = open(OUT / "console_output.txt", "w", encoding="utf-8")
    sys.stdout = Tee(sys.__stdout__, log_file)

    # Figures need matplotlib. If it cannot load (e.g. a Windows Application Control
    # policy blocks its DLL), the search, replanning and tables still run.
    try:
        from warehouse_robot import visualize as viz
    except Exception as exc:                      # noqa: BLE001
        viz = None
        print("WARNING: matplotlib could not be loaded, so figures/GIFs will be skipped.")
        print(f"         Reason: {type(exc).__name__}: {exc}")
        print("         All tasks and tables below still run. See README > Troubleshooting.")

    wh = Warehouse(MAIN_WAREHOUSE, name="Main warehouse")

    # ---------------------------------------------------------------- Task 1
    banner("TASK 1 - WAREHOUSE ENVIRONMENT")
    print(f"Grid size: {wh.rows} rows x {wh.cols} columns | start S = {wh.start} | "
          f"goal G = {wh.goal}")
    print("Moves: Up, Down, Left, Right | entering normal cell = 1, crowded cell = 4")
    print(wh.render())
    print(LEGEND)
    if viz:
        viz.plot_environment(wh, OUT / "01_warehouse_grid.png", args.show)

    # ---------------------------------------------------------------- Task 2
    banner("TASK 2 - PROBLEM FORMULATION")
    problem = WarehouseProblem(wh)
    print(f"State            : robot position (row, col)")
    print(f"Initial state    : {problem.initial_state}  (packing station S)")
    print(f"Actions(s)       : legal moves among Up/Down/Left/Right, e.g. "
          f"Actions{problem.initial_state} = {problem.actions(problem.initial_state)}")
    print(f"Transition model : Result(s, a) = s + delta(a)  e.g. "
          f"Result({problem.initial_state}, 'Right') = "
          f"{problem.result(problem.initial_state, 'Right')}")
    print(f"Goal test        : s == {problem.goal}  (dispatch area G)")
    print(f"Path cost        : sum of costs of cells entered (open = 1, crowded = 4)")
    print(f"Heuristic        : Manhattan distance, h(S) = {problem.heuristic(problem.initial_state)}")

    # ---------------------------------------------------------------- Task 3
    banner("TASK 3 - SEARCH ALGORITHMS (BFS, DFS, GREEDY BEST-FIRST, A*)")
    results = compare_algorithms(wh, args.repeats)
    for res in results:
        print(f"\n--- {res.algorithm} ---")
        if res.found:
            print(f"Route found: {res.moves} moves, total cost {res.cost}, "
                  f"{res.nodes_expanded} nodes expanded")
            print(wh.render(res.path))
            print("Route: " + " -> ".join(f"({r},{c})" for r, c in res.path))
        else:
            print("NO ROUTE FOUND from S to G.")
    print("\n" + LEGEND)
    print("\nWhy Manhattan distance is a lower bound on the remaining travel cost:")
    print("  * Each move changes the row OR the column by exactly 1, so reaching G needs at")
    print("    least |dr| + |dc| moves, whatever obstacles are in the way.")
    print("  * Every move costs at least 1 (open = 1, crowded = 4).")
    print("  => remaining cost >= number of moves >= Manhattan distance, so h never")
    print("     overestimates (admissible). It is also consistent: h(n) <= c(n,n') + h(n').")
    print("\nShort crowded route vs. longer, less costly route:")
    print("  " + shortest_vs_cheapest(results))
    if viz:
        viz.plot_algorithm_routes(wh, results, OUT / "02_algorithm_routes.png", args.show)
    if viz:
        viz.plot_shortest_vs_cheapest(wh, results, OUT / "03_shortest_vs_cheapest.png", args.show)

    # ---------------------------------------------------------------- Task 4
    banner("TASK 4 - TROLLEY DETECTION AND REPLANNING")
    initial = astar(WarehouseProblem(wh))
    trolley_cell = tuple(args.trolley) if args.trolley else None
    true_map, trolley = place_trolley_on_route(wh, initial.path, trolley_cell)
    print(f"Experiment A - trolley placed ON the initial A* route at {trolley}.")
    print("The trolley is in the TRUE map but NOT in the robot's known map.\n")
    print("Robot's known map with its original A* route:")
    print(wh.render(initial.path))
    rep_main = run_with_replanning(true_map, wh)
    print()
    for line in rep_main.log:
        print("  > " + line)
    print("\nTrue map with the route actually driven (X marks where the trolley was detected):")
    print(true_map.render(rep_main.executed_path, {d[0]: "X" for d in rep_main.detections}))
    if viz:
        viz.plot_replanning(true_map, rep_main, trolley, OUT / "04_replanning_success.png",
                            "Experiment A: trolley on the A* route", args.show)

    dead = Warehouse(DEAD_END_WAREHOUSE, name="Dead-end warehouse")
    dead_plan = astar(WarehouseProblem(dead))
    dead_true, dead_trolley = place_trolley_on_route(dead, dead_plan.path, DEAD_END_TROLLEY)
    print(f"\nExperiment B - single-corridor warehouse, trolley at {dead_trolley} "
          f"(no alternative route).")
    print(dead.render(dead_plan.path))
    rep_dead = run_with_replanning(dead_true, dead)
    print()
    for line in rep_dead.log:
        print("  > " + line)
    print(dead_true.render(rep_dead.executed_path, {d[0]: "X" for d in rep_dead.detections}))
    if viz:
        viz.plot_replanning(dead_true, rep_dead, dead_trolley, OUT / "05_replanning_failure.png",
                            "Experiment B: no alternative route", args.show)

    if viz and not args.no_animation:
        print("\nCreating animations (outputs/*.gif) ...")
        viz.animate_replanning(true_map, rep_main, OUT / "06_replanning_animation.gif",
                               "Experiment A", show=args.show)
        viz.animate_replanning(dead_true, rep_dead, OUT / "07_replanning_failure_animation.gif",
                               "Experiment B", show=args.show)

    # ---------------------------------------------------------------- Task 5
    banner("TASK 5 - PERFORMANCE EVALUATION")
    a_rows = algorithm_rows(results)
    print(f"Algorithm comparison on the main warehouse (time = average of {args.repeats} runs):")
    print(format_table(ALGO_HEADERS, a_rows))
    reports = {"A: trolley on A* route": rep_main, "B: dead-end corridor": rep_dead}
    r_rows = replan_rows(reports)
    print("\nTrolley experiments (A* with replanning; nodes expanded summed over all plans):")
    print(format_table(REPLAN_HEADERS, r_rows))
    print("\nFindings:")
    print("  * " + shortest_vs_cheapest(results))
    print("  * A* returned the lowest-cost route; Greedy expanded the fewest nodes but "
          "followed h blindly into the crowded aisle.")
    print("  * DFS found a route but it is long and costly - DFS is neither shortest nor "
          "cheapest.")
    print(f"  * With the trolley, the robot replanned {rep_main.replans} time(s) and still "
          f"reached G (cost {rep_main.total_cost} vs. {initial.cost} planned).")
    print("  * In the dead-end warehouse replanning correctly reported that no route exists.")

    save_csv(OUT / "algorithm_comparison.csv", ALGO_HEADERS, a_rows)
    save_csv(OUT / "replanning_results.csv", REPLAN_HEADERS, r_rows)
    if viz:
        viz.plot_metrics(results, OUT / "08_performance_comparison.png", args.show)
    with open(OUT / "results.md", "w", encoding="utf-8") as f:
        f.write("## Algorithm comparison\n\n" + markdown_table(ALGO_HEADERS, a_rows))
        f.write("\n\n## Trolley / replanning experiments\n\n" + markdown_table(REPLAN_HEADERS, r_rows))
        f.write("\n\n## Shortest vs. cheapest\n\n" + shortest_vs_cheapest(results) + "\n")

    banner("DONE")
    print(f"All figures, tables and this console log are saved in: {OUT}")
    sys.stdout = sys.__stdout__
    log_file.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
