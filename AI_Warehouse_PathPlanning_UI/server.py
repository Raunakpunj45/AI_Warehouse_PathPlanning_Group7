"""
Web UI backend for the warehouse robot.

    python server.py            # starts http://127.0.0.1:8000 and opens the browser
    python server.py --port 9000 --no-browser

Uses only the Python standard library (no Flask, no matplotlib), so it runs on any
machine with Python 3.10+. The frontend lives in ./web and calls these JSON APIs:

    GET  /api/layouts   preset warehouse maps
    POST /api/search    {"layout": [...], "algorithms": [...]}   -> route + metrics per algorithm
    POST /api/replan    {"layout": [...], "auto_trolley": true}   -> trolley detection + replanning
"""

from __future__ import annotations

import argparse
import json
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from warehouse_robot.algorithms import ALGORITHMS, astar, timed
from warehouse_robot.evaluate import shortest_vs_cheapest
from warehouse_robot.grid import OPEN, TROLLEY, Warehouse
from warehouse_robot.layouts import DEAD_END_TROLLEY, DEAD_END_WAREHOUSE, MAIN_WAREHOUSE
from warehouse_robot.problem import WarehouseProblem
from warehouse_robot.replanning import run_with_replanning

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
ALLOWED = set(".C#RSGT")
MAX_SIZE = 40


class ApiError(Exception):
    pass


# ------------------------------------------------------------------ helpers
def parse_layout(raw) -> list[str]:
    if not isinstance(raw, list) or not raw or not all(isinstance(r, str) for r in raw):
        raise ApiError("layout must be a non-empty list of strings")
    if len(raw) > MAX_SIZE or len(raw[0]) > MAX_SIZE:
        raise ApiError(f"grid is limited to {MAX_SIZE} x {MAX_SIZE}")
    if any(len(r) != len(raw[0]) for r in raw):
        raise ApiError("all rows must have the same length")
    bad = {ch for r in raw for ch in r} - ALLOWED
    if bad:
        raise ApiError(f"unknown cell symbols: {''.join(sorted(bad))}")
    for sym, name in (("S", "start"), ("G", "goal")):
        n = sum(r.count(sym) for r in raw)
        if n != 1:
            raise ApiError(f"the grid needs exactly one {name} cell '{sym}' (found {n})")
    return raw


def split_maps(layout: list[str]):
    """True map = layout as drawn. Known map = same, but trolleys removed (robot can't see them)."""
    true_map = Warehouse(layout, "True map")
    known = Warehouse([r.replace(TROLLEY, OPEN) for r in layout], "Known map")
    trolleys = [(r, c) for r, row in enumerate(layout) for c, ch in enumerate(row) if ch == TROLLEY]
    return true_map, known, trolleys


def result_json(res):
    return {"algorithm": res.algorithm, "found": res.found, "path": res.path,
            "moves": res.moves, "cost": res.cost, "nodes_expanded": res.nodes_expanded,
            "time_ms": round(res.time_ms, 4), "explored": res.explored_order}


# --------------------------------------------------------------- endpoints
def api_layouts():
    dead = [list(r) for r in DEAD_END_WAREHOUSE]
    dead[DEAD_END_TROLLEY[0]][DEAD_END_TROLLEY[1]] = TROLLEY
    return {"presets": [
        {"id": "main", "name": "Main warehouse (crowded aisle)", "layout": MAIN_WAREHOUSE},
        {"id": "dead_end", "name": "Dead-end corridor (trolley, no alternative)",
         "layout": ["".join(r) for r in dead]},
    ], "algorithms": list(ALGORITHMS)}


def api_search(body):
    layout = parse_layout(body.get("layout"))
    names = body.get("algorithms") or list(ALGORITHMS)
    unknown = [n for n in names if n not in ALGORITHMS]
    if unknown:
        raise ApiError(f"unknown algorithm(s): {unknown}")
    _, known, trolleys = split_maps(layout)
    problem = WarehouseProblem(known)
    results = [timed(ALGORITHMS[n], problem, repeats=20) for n in names]
    return {"results": [result_json(r) for r in results],
            "verdict": shortest_vs_cheapest(results),
            "note": ("Trolleys are not on the robot's map, so the search ignores them. "
                     "Use the Replanning tab to see them in action.") if trolleys else ""}


def api_replan(body):
    layout = parse_layout(body.get("layout"))
    true_map, known, trolleys = split_maps(layout)
    auto_placed = None
    if not trolleys and body.get("auto_trolley", True):
        plan = astar(WarehouseProblem(known))
        if not plan.found:
            raise ApiError("No route exists, so there is nowhere to place a trolley.")
        if len(plan.path) < 3:
            raise ApiError("The route is too short to place a trolley on it.")
        auto_placed = plan.path[len(plan.path) // 2]
        rows = [list(r) for r in layout]
        rows[auto_placed[0]][auto_placed[1]] = TROLLEY
        layout = ["".join(r) for r in rows]
        true_map, known, trolleys = split_maps(layout)
    rep = run_with_replanning(true_map, known)
    return {"layout": layout, "trolleys": trolleys, "auto_placed": auto_placed,
            "goal_reached": rep.goal_reached, "executed_path": rep.executed_path,
            "plans": [{"from": f, "path": p} for f, p in rep.plans],
            "detections": [{"robot": a, "blocked": b} for a, b in rep.detections],
            "detection_steps": rep.detection_steps, "replans": rep.replans,
            "moves": rep.moves, "total_cost": rep.total_cost,
            "nodes_expanded": rep.nodes_expanded, "time_ms": round(rep.time_ms, 4),
            "message": rep.message, "log": rep.log}


ROUTES = {"/api/search": api_search, "/api/replan": api_replan}


# ------------------------------------------------------------------ server
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt, *args):          # keep the console quiet
        pass

    def _json(self, status, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/api/layouts":
            return self._json(200, api_layouts())
        return super().do_GET()

    def do_POST(self):
        handler = ROUTES.get(self.path)
        if handler is None:
            return self._json(404, {"error": "unknown endpoint"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            return self._json(200, handler(body))
        except ApiError as exc:
            return self._json(400, {"error": str(exc)})
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": f"bad request: {exc}"})
        except Exception as exc:                 # noqa: BLE001
            return self._json(500, {"error": f"server error: {exc}"})


def main():
    ap = argparse.ArgumentParser(description="Warehouse robot web UI")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}"
    print(f"Warehouse robot UI running at {url}  (press Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
