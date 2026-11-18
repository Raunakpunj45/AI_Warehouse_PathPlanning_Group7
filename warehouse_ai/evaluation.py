"""Task 5: performance evaluation and report formatting."""
def compare(results):
    headers = ["Algorithm", "Goal reached", "Moves", "Total cost", "Nodes expanded", "Time (ms)"]
    rows = []
    for x in results:
        rows.append([
            x["algorithm"], "Yes" if x["goal_reached"] else "No",
            x["moves"] if x["moves"] is not None else "-",
            x["path_cost"] if x["path_cost"] is not None else "-",
            x["nodes_expanded"], f'{x["execution_time_ms"]:.3f}'
        ])
    widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
    line = "+-" + "-+-".join("-"*w for w in widths) + "-+"
    out = [line, "| " + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))) + " |", line]
    for row in rows:
        out.append("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |")
    out.append(line)
    return "\n".join(out)

def shortest_vs_cheapest(results):
    valid = [r for r in results if r["goal_reached"]]
    if not valid:
        return "No algorithm reached the goal."
    shortest = min(valid, key=lambda r: r["moves"])
    cheapest = min(valid, key=lambda r: r["path_cost"])
    if shortest["algorithm"] == cheapest["algorithm"]:
        return (f'{shortest["algorithm"]} produced both the fewest moves '
                f'({shortest["moves"]}) and lowest cost ({shortest["path_cost"]}).')
    return (f'The fewest-move route was {shortest["algorithm"]} '
            f'({shortest["moves"]} moves, cost {shortest["path_cost"]}), while the lowest-cost '
            f'route was {cheapest["algorithm"]} ({cheapest["moves"]} moves, cost {cheapest["path_cost"]}). '
            'Therefore, the route with the fewest moves is not necessarily the cheapest.')
