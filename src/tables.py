import pandas as pd
import numpy as np
import torch


def full_node_table(g, node_metadata):
    deg = g.in_degrees() + g.out_degrees()
    rows = []

    for i in range(g.num_nodes()):
        rows.append({
            "node_id": i,
            "ASN": int(g.ndata["asn"][i]),
            "Nombre": node_metadata.get("name", {}).get(i, ""),
            "In-degree": int(g.in_degrees()[i]),
            "Out-degree": int(g.out_degrees()[i]),
            "Degree": int(deg[i]),
            "Path occurrences": int(
                g.ndata["path_occurrences"][i]
                if "path_occurrences" in g.ndata else 0
            ),
        })

    return pd.DataFrame(rows)


def top_k_by_path_occurrences(g, node_metadata, k=20):
    df = full_node_table(g, node_metadata)
    return df.sort_values("Path occurrences", ascending=False).head(k)


def critical_asn_score(g, node_metadata):
    deg = g.in_degrees() + g.out_degrees()
    rows = []

    for i in range(g.num_nodes()):
        score = (
            np.log1p(int(deg[i])) +
            np.log1p(
                int(g.ndata["path_occurrences"][i])
                if "path_occurrences" in g.ndata else 0
            )
        )

        rows.append({
            "ASN": int(g.ndata["asn"][i]),
            "Nombre": node_metadata.get("name", {}).get(i, ""),
            "Score": score,
            "Degree": int(deg[i]),
            "Path occurrences": int(
                g.ndata["path_occurrences"][i]
                if "path_occurrences" in g.ndata else 0
            ),
        })

    return pd.DataFrame(rows).sort_values("Score", ascending=False)
