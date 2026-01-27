import pandas as pd
import torch
import dgl


def load_graph_from_csv(nodes_csv_path, edges_csv_path):
    """
    Carga un grafo DGL desde CSV.

    Retorna:
        g : DGLGraph
        node_metadata : dict
            Información NO numérica por nodo (ej: nombre ASN)
    """

    # -------------------------
    # Leer CSVs
    # -------------------------
    nodes_df = pd.read_csv(nodes_csv_path)
    edges_df = pd.read_csv(edges_csv_path)

    # -------------------------
    # Crear grafo
    # -------------------------
    g = dgl.graph(
        (edges_df["src_id"].values, edges_df["dst_id"].values),
        num_nodes=len(nodes_df)
    )

    # -------------------------
    # Atributos NUMÉRICOS de nodo
    # -------------------------
    g.ndata["asn"] = torch.tensor(
        nodes_df["asn"].values,
        dtype=torch.int64
    )

    if "in_degree" in nodes_df.columns:
        g.ndata["in_degree"] = torch.tensor(nodes_df["in_degree"].values)

    if "out_degree" in nodes_df.columns:
        g.ndata["out_degree"] = torch.tensor(nodes_df["out_degree"].values)

    if "path_occurrences" in nodes_df.columns:
        g.ndata["path_occurrences"] = torch.tensor(
            nodes_df["path_occurrences"].values
        )

    # -------------------------
    # Atributos de arista
    # -------------------------
    if "weight" in edges_df.columns:
        g.edata["weight"] = torch.tensor(edges_df["weight"].values)

    # -------------------------
    # Metadata NO numérica
    # (clave: node_id)
    # -------------------------
    node_metadata = {
        "name": nodes_df["name"].fillna("").astype(str).to_dict()
    }

    return g, node_metadata
