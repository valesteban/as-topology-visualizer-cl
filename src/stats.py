import torch


def graph_basic_stats(g):
    in_deg = g.in_degrees()
    out_deg = g.out_degrees()
    deg = in_deg + out_deg

    return {
        "nodes": g.num_nodes(),
        "edges": g.num_edges(),
        "avg_in_degree": float(in_deg.float().mean()),
        "avg_out_degree": float(out_deg.float().mean()),
        "avg_degree": float(deg.float().mean()),
        "max_degree": int(deg.max()),
    }
