"""Member 1 entry point: inspect warehouse and problem formulation."""
from warehouse_ai.environment import Warehouse
if __name__ == "__main__":
    env = Warehouse()
    env.display()
    print("\nProblem formulation")
    for k, v in env.problem_formulation().items():
        print(f"{k}: {v}")
