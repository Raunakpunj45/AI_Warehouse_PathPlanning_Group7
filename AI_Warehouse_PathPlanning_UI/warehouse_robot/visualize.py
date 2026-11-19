"""Matplotlib visualisations: labelled grids, routes, metric charts and a replanning animation."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from .algorithms import SearchResult
from .grid import CROWDED, GOAL, OPEN, RESTRICTED, SHELF, START, TROLLEY, Warehouse
from .replanning import ReplanReport

# cell symbol -> (colour index, label)
CODES = {OPEN: 0, START: 0, GOAL: 0, CROWDED: 1, SHELF: 2, RESTRICTED: 3, TROLLEY: 4}
COLORS = ["#f7f7f2", "#f6c177", "#5b4a3f", "#e06c75", "#9b59b6"]
CMAP = ListedColormap(COLORS)
ALGO_COLORS = {"BFS": "#1f77b4", "DFS": "#7f7f7f", "Greedy Best-First": "#ff7f0e", "A*": "#2ca02c"}

LEGEND_HANDLES = [
    Patch(facecolor=COLORS[0], edgecolor="#999", label="Open aisle (cost 1)"),
    Patch(facecolor=COLORS[1], edgecolor="#999", label="Crowded aisle (cost 4)"),
    Patch(facecolor=COLORS[2], edgecolor="#999", label="Shelf (blocked)"),
    Patch(facecolor=COLORS[3], edgecolor="#999", label="Restricted zone (blocked)"),
    Patch(facecolor=COLORS[4], edgecolor="#999", label="Trolley (blocked)"),
]


def _grid_array(wh: Warehouse) -> np.ndarray:
    return np.array([[CODES[ch] for ch in row] for row in wh.grid])


def draw_grid(ax, wh: Warehouse, title: str = "", hide: set | None = None) -> None:
    """Draw the warehouse. Cells in `hide` are drawn as open (used for 'unknown' trolleys)."""
    arr = _grid_array(wh)
    for (r, c) in hide or set():
        arr[r, c] = 0
    ax.imshow(arr, cmap=CMAP, vmin=0, vmax=len(COLORS) - 1)
    ax.set_xticks(np.arange(-.5, wh.cols, 1), minor=True)
    ax.set_yticks(np.arange(-.5, wh.rows, 1), minor=True)
    ax.grid(which="minor", color="#bbbbbb", linewidth=0.6)
    ax.tick_params(which="minor", length=0)
    ax.set_xticks(range(wh.cols))
    ax.set_yticks(range(wh.rows))
    ax.tick_params(labelsize=7)
    for r in range(wh.rows):
        for c in range(wh.cols):
            ch = wh.grid[r][c]
            if ch == CROWDED:
                ax.text(c, r, "C", ha="center", va="center", fontsize=7, color="#8a5a00")
            elif ch == RESTRICTED:
                ax.text(c, r, "R", ha="center", va="center", fontsize=7, color="white")
            elif ch == TROLLEY and (r, c) not in (hide or set()):
                ax.text(c, r, "T", ha="center", va="center", fontsize=9, color="white",
                        fontweight="bold")
    sr, sc = wh.start
    gr, gc = wh.goal
    ax.scatter(sc, sr, s=260, marker="s", c="#27ae60", edgecolors="black", zorder=5)
    ax.text(sc, sr, "S", ha="center", va="center", color="white", fontweight="bold", zorder=6)
    ax.scatter(gc, gr, s=260, marker="s", c="#2980b9", edgecolors="black", zorder=5)
    ax.text(gc, gr, "G", ha="center", va="center", color="white", fontweight="bold", zorder=6)
    ax.set_title(title, fontsize=10)


def draw_path(ax, path, color, label=None, lw=3, ls="-", offset=0.0, alpha=0.9):
    if not path:
        return
    ys = [r + offset for r, _ in path]
    xs = [c + offset for _, c in path]
    ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls, label=label, alpha=alpha,
            solid_capstyle="round", zorder=4)


def plot_environment(wh: Warehouse, out: Path, show=False) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    draw_grid(ax, wh, f"{wh.name}: packing station S -> dispatch area G")
    ax.legend(handles=LEGEND_HANDLES, loc="upper center", bbox_to_anchor=(0.5, -0.06),
              ncol=3, fontsize=8, frameon=False)
    _save(fig, out, show)


def plot_algorithm_routes(wh: Warehouse, results: list[SearchResult], out: Path, show=False):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    for ax, res in zip(axes.flat, results):
        color = ALGO_COLORS.get(res.algorithm, "black")
        if res.found:
            explored = res.explored_order
            if explored:
                ax.scatter([c for _, c in explored], [r for r, _ in explored], s=14,
                           c="#555", alpha=0.35, zorder=3, label="expanded node")
            title = (f"{res.algorithm}: {res.moves} moves | cost {res.cost} | "
                     f"{res.nodes_expanded} nodes expanded")
        else:
            title = f"{res.algorithm}: NO ROUTE FOUND"
        draw_grid(ax, wh, title)
        draw_path(ax, res.path, color, label="route")
        ax.legend(loc="lower right", fontsize=7)
    fig.legend(handles=LEGEND_HANDLES, loc="lower center", ncol=5, fontsize=8, frameon=False)
    fig.suptitle("Route returned by each search algorithm (same warehouse)", fontsize=13)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96), h_pad=3)
    _save(fig, out, show)


def plot_shortest_vs_cheapest(wh: Warehouse, results: list[SearchResult], out: Path, show=False):
    by = {r.algorithm: r for r in results}
    bfs, ast = by["BFS"], by["A*"]
    fig, ax = plt.subplots(figsize=(10, 6.5))
    draw_grid(ax, wh, "Short crowded route (BFS) vs. longer, less costly route (A*)")
    draw_path(ax, bfs.path, ALGO_COLORS["BFS"], offset=0.12,
              label=f"BFS - fewest moves: {bfs.moves} moves, cost {bfs.cost}")
    draw_path(ax, ast.path, ALGO_COLORS["A*"], offset=-0.12,
              label=f"A* - lowest cost: {ast.moves} moves, cost {ast.cost}")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=1, fontsize=9,
              frameon=False)
    _save(fig, out, show)


def plot_metrics(results: list[SearchResult], out: Path, show=False):
    names = [r.algorithm for r in results]
    colors = [ALGO_COLORS.get(n, "black") for n in names]
    metrics = [("Path length (moves)", [r.moves or 0 for r in results]),
               ("Total path cost", [r.cost or 0 for r in results]),
               ("Nodes expanded", [r.nodes_expanded for r in results]),
               ("Execution time (ms)", [r.time_ms for r in results])]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4))
    for ax, (title, vals) in zip(axes, metrics):
        bars = ax.bar(names, vals, color=colors)
        ax.set_title(title, fontsize=10)
        ax.tick_params(axis="x", labelrotation=20, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                    f"{v:.3f}" if isinstance(v, float) else str(v),
                    ha="center", va="bottom", fontsize=8)
    fig.suptitle("Performance comparison", fontsize=13)
    fig.tight_layout()
    _save(fig, out, show)


def plot_replanning(true_map: Warehouse, report: ReplanReport, trolley: tuple, out: Path,
                    title: str, show=False):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.8))
    # Left: what the robot believes + its original plan
    draw_grid(axes[0], true_map, "1) Robot's known map (trolley unknown) + original A* plan",
              hide={trolley})
    draw_path(axes[0], report.original_plan, "#2ca02c", label="original A* plan")
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), fontsize=8, frameon=False)
    # Right: reality, detection and revised route
    ax = axes[1]
    draw_grid(ax, true_map, "2) Trolley detected -> map updated -> A* replanned")
    draw_path(ax, report.original_plan, "#2ca02c", ls="--", lw=2, alpha=0.5,
              label="original plan (abandoned)")
    for start_cell, plan in report.plans[1:]:
        if plan:
            draw_path(ax, plan, "#e67e22", lw=3, label="revised A* plan")
    draw_path(ax, report.executed_path, "#2c3e50", lw=1.5, offset=0.15,
              label="route actually driven")
    for robot_at, blocked in report.detections:
        ax.scatter(robot_at[1], robot_at[0], s=200, c="#f1c40f", edgecolors="black",
                   marker="o", zorder=7, label=f"robot detects trolley at {blocked}")
        ax.annotate("", xy=(blocked[1], blocked[0]), xytext=(robot_at[1], robot_at[0]),
                    arrowprops=dict(arrowstyle="->", color="red", lw=2), zorder=8)
    if not report.goal_reached:
        ax.set_title("2) Trolley detected -> map updated -> A* found NO ALTERNATIVE ROUTE",
                     fontsize=10, color="#c0392b", fontweight="bold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8,
              frameon=False)
    fig.suptitle(f"{title} - replans: {report.replans} | goal reached: "
                 f"{'YES' if report.goal_reached else 'NO'}", fontsize=13)
    fig.tight_layout()
    _save(fig, out, show)


def animate_replanning(true_map: Warehouse, report: ReplanReport, out: Path, title: str,
                       fps: int = 4, show=False):
    """GIF: robot follows its plan, sees the trolley, replans and continues (or stops)."""
    hidden = {blocked for _, blocked in report.detections}
    frames = []          # (step index, plan shown, cells still unknown, event)
    plan_no = 0
    unknown = set(hidden)
    det_at = {}
    for k, step in enumerate(report.detection_steps):
        det_at.setdefault(step, []).append(k)
    for idx in range(len(report.executed_path)):
        frames.append((idx, report.plans[plan_no][1], set(unknown), None))
        for k in det_at.get(idx, []):
            blocked = report.detections[k][1]
            unknown.discard(blocked)
            frames += [(idx, report.plans[plan_no][1], set(unknown), ("detect", blocked))] * 3
            plan_no += 1
            new_plan = report.plans[plan_no][1]
            event = ("replanned", None) if new_plan else ("failed", None)
            frames += [(idx, new_plan, set(unknown), event)] * (3 if new_plan else 8)
    frames += [frames[-1]] * 6

    fig, ax = plt.subplots(figsize=(9, 6))

    def update(i):
        idx, plan, unk, event = frames[i]
        ax.clear()
        draw_grid(ax, true_map, "", hide=unk)
        draw_path(ax, plan, "#2ca02c", lw=2.5, alpha=0.6)
        draw_path(ax, report.executed_path[: idx + 1], "#2c3e50", lw=3)
        r, c = report.executed_path[idx]
        ax.scatter(c, r, s=300, c="#f1c40f", edgecolors="black", zorder=9)
        ax.text(c, r, "X", ha="center", va="center", fontweight="bold", zorder=10)
        status = f"step {idx}"
        if event and event[0] == "detect":
            status += f" | TROLLEY DETECTED at {event[1]} - updating map"
            ax.annotate("", xy=(event[1][1], event[1][0]), xytext=(c, r),
                        arrowprops=dict(arrowstyle="->", color="red", lw=2.5), zorder=11)
        elif event and event[0] == "replanned":
            status += " | replanned with A* from current position"
        elif event and event[0] == "failed":
            status += " | NO ALTERNATIVE ROUTE - robot stops"
        elif report.executed_path[idx] == true_map.goal:
            status += " | GOAL REACHED"
        ax.set_title(f"{title}: {status}", fontsize=10)

    anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000 // fps)
    anim.save(out, writer=animation.PillowWriter(fps=fps))
    if show:
        plt.show()
    plt.close(fig)


def _save(fig, out: Path, show: bool):
    fig.savefig(out, dpi=130, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
