# src/merge/merge_graph.py

from pathlib import Path
import pandas as pd


def merge_graphs_by_asn(
    bgp_nodes_csv: Path,
    bgp_edges_csv: Path,
    ripe_nodes_csv: Path,
    ripe_edges_csv: Path,
    out_nodes_csv: Path,
    out_edges_csv: Path,
):
    """
    Merge de dos grafos AS-level (BGP + RIPE Atlas) usando ASN como llave.

    - Los nodos se unen por ASN
    - Las aristas se combinan
    - Si una arista aparece en ambos grafos, se suman los pesos
    """

    # --------------------------------------------------
    # 1. Cargar CSVs
    # --------------------------------------------------
    bgp_nodes = pd.read_csv(bgp_nodes_csv)
    bgp_edges = pd.read_csv(bgp_edges_csv)

    ripe_nodes = pd.read_csv(ripe_nodes_csv)
    ripe_edges = pd.read_csv(ripe_edges_csv)

    # --------------------------------------------------
    # 2. Crear mapping ASN → nuevo node_id
    # --------------------------------------------------
    all_asns = sorted(
        set(bgp_nodes["asn"]).union(set(ripe_nodes["asn"]))
    )

    asn_to_id = {asn: i for i, asn in enumerate(all_asns)}

    merged_nodes = pd.DataFrame({
        "node_id": list(asn_to_id.values()),
        "asn": list(asn_to_id.keys())
    })

    # --------------------------------------------------
    # 3. Helper: convertir edges a ASN-space
    # --------------------------------------------------
    def edges_to_asn_space(edges_df, nodes_df):
        node_id_to_asn = dict(
            zip(nodes_df["node_id"], nodes_df["asn"])
        )

        edges_df = edges_df.copy()
        edges_df["asn_src"] = edges_df["src_id"].map(node_id_to_asn)
        edges_df["asn_dst"] = edges_df["dst_id"].map(node_id_to_asn)

        edges_df = edges_df.dropna(subset=["asn_src", "asn_dst"])

        return edges_df[["asn_src", "asn_dst", "weight"]]

    bgp_asn_edges = edges_to_asn_space(bgp_edges, bgp_nodes)
    ripe_asn_edges = edges_to_asn_space(ripe_edges, ripe_nodes)

    # --------------------------------------------------
    # 4. Combinar aristas y sumar pesos
    # --------------------------------------------------
    merged_edges_asn = (
        pd.concat([bgp_asn_edges, ripe_asn_edges])
        .groupby(["asn_src", "asn_dst"], as_index=False)["weight"]
        .sum()
    )

    # --------------------------------------------------
    # 5. Volver a node_id-space
    # --------------------------------------------------
    merged_edges = pd.DataFrame({
        "src_id": merged_edges_asn["asn_src"].map(asn_to_id),
        "dst_id": merged_edges_asn["asn_dst"].map(asn_to_id),
        "weight": merged_edges_asn["weight"].astype(int)
    })

    # --------------------------------------------------
    # 6. Guardar resultados
    # --------------------------------------------------
    out_nodes_csv.parent.mkdir(parents=True, exist_ok=True)
    out_edges_csv.parent.mkdir(parents=True, exist_ok=True)

    merged_nodes.to_csv(out_nodes_csv, index=False)
    merged_edges.to_csv(out_edges_csv, index=False)

    return merged_nodes, merged_edges
