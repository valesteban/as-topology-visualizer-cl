import pandas as pd
from src.stats import graph_basic_stats


def compare_graphs(graphs: dict):
    """
    graphs = {
        "BGP": g_bgp,
        "RIPE Atlas": g_ripe,
        "Merged": g_merged
    }
    """
    rows = []

    for name, g in graphs.items():
        stats = graph_basic_stats(g)
        stats["Graph"] = name
        rows.append(stats)

    return pd.DataFrame(rows).set_index("Graph")
