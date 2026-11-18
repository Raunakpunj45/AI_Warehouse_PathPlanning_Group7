"""Member 4 entry point: A* and weighted path costs."""
from warehouse_ai.environment import Warehouse
from warehouse_ai.search import astar
if __name__ == "__main__":
    env = Warehouse()
    result = astar(env)
    print(result)
    env.display(result["path"], title="A* minimum-cost route")
