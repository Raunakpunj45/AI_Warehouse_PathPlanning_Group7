"""Members 2, 3 and 4: BFS, DFS, Greedy Best-First Search and A*."""
from collections import deque
from heapq import heappush, heappop
from itertools import count
from time import perf_counter

def reconstruct_path(parent, start, goal):
    if goal != start and goal not in parent:
        return []
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    return path if path and path[0] == start else []

def _result(name, path, expanded, elapsed, env):
    return {
        "algorithm": name,
        "goal_reached": bool(path and path[-1] == env.goal),
        "path": path,
        "moves": max(0, len(path)-1) if path else None,
        "path_cost": env.path_cost(path) if path else None,
        "nodes_expanded": expanded,
        "execution_time_ms": elapsed * 1000
    }

def bfs(env, start=None, goal=None, extra_blocked=None):
    start, goal = start or env.start, goal or env.goal
    t0 = perf_counter()
    queue = deque([start]); parent = {start: None}; expanded = 0
    while queue:
        cur = queue.popleft(); expanded += 1
        if cur == goal: break
        for nxt in env.neighbors(cur, extra_blocked):
            if nxt not in parent:
                parent[nxt] = cur
                queue.append(nxt)
    elapsed = perf_counter() - t0
    return _result("BFS", reconstruct_path(parent, start, goal), expanded, elapsed, _GoalView(env, goal))

def dfs(env, start=None, goal=None, extra_blocked=None):
    start, goal = start or env.start, goal or env.goal
    t0 = perf_counter()
    stack = [start]; parent = {start: None}; expanded = 0
    while stack:
        cur = stack.pop(); expanded += 1
        if cur == goal: break
        # Reverse to preserve the same intuitive order under a LIFO stack.
        for nxt in reversed(env.neighbors(cur, extra_blocked)):
            if nxt not in parent:
                parent[nxt] = cur
                stack.append(nxt)
    elapsed = perf_counter() - t0
    return _result("DFS", reconstruct_path(parent, start, goal), expanded, elapsed, _GoalView(env, goal))

def greedy_best_first(env, start=None, goal=None, extra_blocked=None):
    start, goal = start or env.start, goal or env.goal
    h = lambda p: abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    t0 = perf_counter()
    serial = count(); heap = [(h(start), next(serial), start)]
    parent = {start: None}; visited = set(); expanded = 0
    while heap:
        _, _, cur = heappop(heap)
        if cur in visited: continue
        visited.add(cur); expanded += 1
        if cur == goal: break
        for nxt in env.neighbors(cur, extra_blocked):
            if nxt not in parent:
                parent[nxt] = cur
                heappush(heap, (h(nxt), next(serial), nxt))
    elapsed = perf_counter() - t0
    return _result("Greedy Best-First", reconstruct_path(parent, start, goal), expanded, elapsed, _GoalView(env, goal))

def astar(env, start=None, goal=None, extra_blocked=None):
    start, goal = start or env.start, goal or env.goal
    h = lambda p: abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    t0 = perf_counter()
    serial = count(); heap = [(h(start), next(serial), 0, start)]
    parent = {start: None}; best_g = {start: 0}; expanded = 0
    while heap:
        f, _, g, cur = heappop(heap)
        if g != best_g.get(cur): continue
        expanded += 1
        if cur == goal: break
        for nxt in env.neighbors(cur, extra_blocked):
            new_g = g + env.step_cost(nxt)
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                parent[nxt] = cur
                heappush(heap, (new_g + h(nxt), next(serial), new_g, nxt))
    elapsed = perf_counter() - t0
    return _result("A*", reconstruct_path(parent, start, goal), expanded, elapsed, _GoalView(env, goal))

class _GoalView:
    """Allows result metrics to use a temporary goal during replanning."""
    def __init__(self, env, goal):
        self._env, self.goal = env, goal
    def path_cost(self, path):
        return self._env.path_cost(path)
