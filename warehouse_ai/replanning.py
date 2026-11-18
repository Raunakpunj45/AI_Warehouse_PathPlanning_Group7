"""Member 5: hidden trolley discovery, map update and A* replanning."""
from .search import astar

def demonstrate_trolley(env):
    initial = astar(env)
    if not initial["goal_reached"] or len(initial["path"]) < 3:
        return {"initial": initial, "trolley": None, "replanned": None, "replans": 0,
                "message": "Initial route is unavailable; trolley experiment cannot run."}

    # Select a route cell after the start and before the goal.
    trolley = initial["path"][min(5, len(initial["path"])-2)]
    # The trolley is intentionally absent from the robot's initial known map.
    known_map_blocked = set()
    robot_position = env.start
    revised = None
    replan_count = 0
    events = []

    # Robot follows its planned route and detects the trolley before entering it.
    for next_cell in initial["path"][1:]:
        if next_cell == trolley:
            events.append(f"Trolley detected at {trolley} before entering the cell.")
            known_map_blocked.add(trolley)
            replan_count += 1
            revised = astar(env, start=robot_position, goal=env.goal,
                            extra_blocked=known_map_blocked)
            break
        robot_position = next_cell

    return {
        "initial": initial,
        "trolley": trolley,
        "robot_position_at_detection": robot_position,
        "replanned": revised,
        "replans": replan_count,
        "events": events,
        "message": ("Alternative route found." if revised and revised["goal_reached"]
                    else "No alternative route exists.")
    }
