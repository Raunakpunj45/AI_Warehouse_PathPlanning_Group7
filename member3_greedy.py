"""Member 3 entry point: Greedy Best-First Search and heuristic."""
from warehouse_ai.environment import Warehouse
from warehouse_ai.search import greedy_best_first
if __name__ == "__main__":
    env = Warehouse()
    result = greedy_best_first(env)
    print(result)
    print("Manhattan distance is a lower bound on number of moves.")
    env.display(result["path"], title="Greedy Best-First route")
