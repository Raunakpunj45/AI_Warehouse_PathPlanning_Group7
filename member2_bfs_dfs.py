"""Member 2 entry point: run BFS and DFS."""
from warehouse_ai.environment import Warehouse
from warehouse_ai.search import bfs, dfs
if __name__ == "__main__":
    env = Warehouse()
    for fn in (bfs, dfs):
        result = fn(env)
        print(result["algorithm"], result)
        env.display(result["path"], title=result["algorithm"])
