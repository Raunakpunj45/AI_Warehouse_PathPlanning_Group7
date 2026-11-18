"""Member 5 entry point: trolley detection and replanning."""
from warehouse_ai.environment import Warehouse
from warehouse_ai.replanning import demonstrate_trolley
if __name__ == "__main__":
    env = Warehouse()
    result = demonstrate_trolley(env)
    print(result)
    if result["trolley"] is not None:
        env.display(result["initial"]["path"], {result["trolley"]}, "Original route and trolley")
        if result["replanned"] and result["replanned"]["goal_reached"]:
            env.display(result["replanned"]["path"], {result["trolley"]}, "Replanned route")
