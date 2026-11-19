"""Task 5 - Performance evaluation: comparison tables (console, CSV and Markdown)."""

from __future__ import annotations

import csv
from pathlib import Path

from .algorithms import ALGORITHMS, SearchResult, timed
from .grid import Warehouse
from .problem import WarehouseProblem
from .replanning import ReplanReport

ALGO_HEADERS = ["Algorithm", "Goal reached", "Path length (moves)", "Total path cost",
                "Nodes expanded", "Execution time (ms)"]
REPLAN_HEADERS = ["Scenario", "Goal reached", "Path length (moves)", "Total path cost",
                  "Nodes expanded", "Execution time (ms)", "Replans"]


def compare_algorithms(warehouse: Warehouse, repeats: int = 30) -> list[SearchResult]:
    problem = WarehouseProblem(warehouse)
    return [timed(fn, problem, repeats) for fn in ALGORITHMS.values()]


def algorithm_rows(results: list[SearchResult]) -> list[list[str]]:
    return [[r.algorithm, "Yes" if r.found else "No",
             str(r.moves) if r.found else "-", str(r.cost) if r.found else "-",
             str(r.nodes_expanded), f"{r.time_ms:.3f}"] for r in results]


def replan_rows(reports: dict[str, ReplanReport]) -> list[list[str]]:
    return [[name, "Yes" if rep.goal_reached else "No", str(rep.moves), str(rep.total_cost),
             str(rep.nodes_expanded), f"{rep.time_ms:.3f}", str(rep.replans)]
            for name, rep in reports.items()]


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Plain-ASCII table (works in every terminal, including Windows cmd)."""
    widths = [max(len(h), *(len(row[i]) for row in rows)) for i, h in enumerate(headers)]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    fmt = lambda cells: "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"
    return "\n".join([sep, fmt(headers), sep.replace("-", "="), *map(fmt, rows), sep])


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


def save_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def shortest_vs_cheapest(results: list[SearchResult]) -> str:
    """Answer: did the route with the fewest moves also have the lowest cost?"""
    found = [r for r in results if r.found]
    if not found:
        return "No algorithm found a route."
    fewest = min(found, key=lambda r: (r.moves, r.cost))
    cheapest = min(found, key=lambda r: (r.cost, r.moves))
    if fewest.cost == cheapest.cost:
        return (f"The shortest route ({fewest.moves} moves, by {fewest.algorithm}) was also the "
                f"cheapest (cost {fewest.cost}).")
    return (f"NO - the shortest route was NOT the cheapest. {fewest.algorithm} found the "
            f"fewest moves ({fewest.moves} moves) but it crosses crowded cells, so it costs "
            f"{fewest.cost}. {cheapest.algorithm} took {cheapest.moves} moves "
            f"({cheapest.moves - fewest.moves} more) but its cost is only {cheapest.cost} "
            f"({fewest.cost - cheapest.cost} less), because it avoids the crowded aisle.")
