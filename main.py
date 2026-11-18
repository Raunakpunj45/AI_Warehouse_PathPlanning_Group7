"""Integrated runnable demonstration for the AI Warehouse Robot assignment."""
from warehouse_ai.environment import Warehouse
from warehouse_ai.search import bfs, dfs, greedy_best_first, astar
from warehouse_ai.replanning import demonstrate_trolley
from warehouse_ai.evaluation import compare, shortest_vs_cheapest
from pathlib import Path

def main():
    env = Warehouse()
    output = []
    def emit(s=""):
        print(s); output.append(str(s))

    emit("="*72)
    emit("AI-BASED ROUTE PLANNING FOR A WAREHOUSE DELIVERY ROBOT")
    emit("="*72)
    env.display()
    emit("\nTASK 2 - SEARCH PROBLEM FORMULATION")
    for key, value in env.problem_formulation().items():
        emit(f"{key}: {value}")

    emit("\nTASK 3 - FOUR SEARCH ALGORITHMS")
    results = [bfs(env), dfs(env), greedy_best_first(env), astar(env)]
    for result in results:
        emit(f'\n{result["algorithm"]}:')
        emit(f'Goal reached: {result["goal_reached"]}')
        emit(f'Moves: {result["moves"]}; total cost: {result["path_cost"]}')
        emit(f'Nodes expanded: {result["nodes_expanded"]}; time: {result["execution_time_ms"]:.3f} ms')
        if result["path"]:
            env.display(result["path"], title=f'{result["algorithm"]} route')
        else:
            emit("No route found.")

    emit("\nTASK 3 - SHORTER CROWDED ROUTE VS LONGER CHEAPER ROUTE")
    # A small controlled map isolates the weighted-cost trade-off.
    from warehouse_ai.environment import Warehouse as Grid
    tradeoff = Grid(rows=7, cols=7, start=(3, 0), goal=(3, 6))
    tradeoff.shelves = set()
    tradeoff.restricted = set()
    tradeoff.crowded = {(3, c) for c in range(1, 6)}
    short_route = bfs(tradeoff)
    low_cost_route = astar(tradeoff)
    emit(f"Fewest-move route (BFS): {short_route['moves']} moves, cost {short_route['path_cost']}")
    emit(f"Lowest-cost route (A*): {low_cost_route['moves']} moves, cost {low_cost_route['path_cost']}")
    tradeoff.display(short_route["path"], title="Short route through crowded aisle")
    tradeoff.display(low_cost_route["path"], title="Longer route avoiding crowded aisle")
    emit("This controlled test shows why minimum distance and minimum weighted cost can differ.")

    emit("\nTASK 5 - PERFORMANCE COMPARISON")
    emit(compare(results))
    emit(shortest_vs_cheapest(results))

    emit("\nTASK 4 - HIDDEN TROLLEY AND DYNAMIC REPLANNING")
    demo = demonstrate_trolley(env)
    emit(f'Original A* route: {demo["initial"]["path"]}')
    if demo["trolley"] is not None:
        emit(f'Trolley location (hidden initially): {demo["trolley"]}')
        emit(f'Robot position at detection: {demo["robot_position_at_detection"]}')
        for event in demo["events"]: emit(event)
        emit(f'Replans performed: {demo["replans"]}')
        if demo["replanned"]:
            emit(f'Replanning result: {demo["message"]}')
            emit(f'Revised route: {demo["replanned"]["path"]}')
            env.display(demo["initial"]["path"], extra_blocked={demo["trolley"]},
                        title="Original route with detected trolley")
            if demo["replanned"]["goal_reached"]:
                env.display(demo["replanned"]["path"], extra_blocked={demo["trolley"]},
                            title="Revised route after replanning")
            else:
                emit("No alternative route exists.")
    else:
        emit(demo["message"])

    emit("\nHEURISTIC NOTE")
    emit("Manhattan distance h = |row-goal_row| + |col-goal_col|.")
    emit("Each move changes one coordinate by exactly one, so at least h moves remain.")
    emit("Every legal move costs at least 1 (crowded cells cost 4), hence h never")
    emit("overestimates the remaining weighted path cost. It is an admissible lower bound.")
    emit("\nEXPERIMENT NOTE")
    emit("BFS minimizes number of moves, not weighted cost. DFS depends on neighbor order.")
    emit("Greedy prioritizes only h and is not guaranteed to find a least-cost path.")
    emit("A* uses f=g+h and, with this admissible heuristic and positive costs, finds")
    emit("a minimum-cost route on this grid.")
    out_path = Path("outputs") / "run_output.txt"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text("\n".join(output), encoding="utf-8")
    print(f"\nFull run log saved to: {out_path}")

if __name__ == "__main__":
    main()
