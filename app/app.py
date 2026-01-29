import sys
from pathlib import Path

# --------------------------------------------------
# PYTHONPATH
# --------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# --------------------------------------------------
# Imports
# --------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import torch

from src.io.load_csv_graph import load_graph_from_csv

# --------------------------------------------------
# Utils
# --------------------------------------------------
def graph_basic_stats(g):
    return {
        "nodes": g.num_nodes(),
        "edges": g.num_edges(),
        "avg_in_degree": float(torch.mean(g.in_degrees().float())),
        "avg_out_degree": float(torch.mean(g.out_degrees().float())),
        "max_degree": int(torch.max(g.in_degrees() + g.out_degrees())),
    }


def top_k_nodes_by_degree(g, node_metadata, k=10):
    deg = g.in_degrees() + g.out_degrees()

    rows = []
    for i in range(g.num_nodes()):
        rows.append({
            "ASN": int(g.ndata["asn"][i]),
            "Nombre": node_metadata["name"].get(i, "Nombre no disponible"),
            "Degree": int(deg[i])
        })

    df = pd.DataFrame(rows)
    return df.sort_values("Degree", ascending=False).head(k)


def ego_subgraph_by_asn(g, target_asn, hops=1):
    asns = g.ndata["asn"].numpy()
    idx = np.where(asns == target_asn)[0]

    if len(idx) == 0:
        return None, None

    center = int(idx[0])
    visited = {center}
    frontier = {center}

    for _ in range(hops):
        next_frontier = set()
        for u in frontier:
            next_frontier.update(g.successors(u).tolist())
            next_frontier.update(g.predecessors(u).tolist())
        frontier = next_frontier - visited
        visited |= frontier

    return g.subgraph(list(visited)), center


# --------------------------------------------------
# UI
# --------------------------------------------------
st.set_page_config(
    page_title="AS Topology Visualizer",
    layout="wide"
)

st.title("🌐 AS Topology Visualizer — Chile")
st.caption("Topología AS-level construida desde BGP y RIPE Atlas")

# --------------------------------------------------
# Selección de grafo
# --------------------------------------------------
GRAPH_PATHS = {
    "BGP": {
        "nodes": Path("data/csv/bgp/nodes.csv"),
        "edges": Path("data/csv/bgp/edges.csv"),
    },
    "RIPE Atlas": {
        "nodes": Path("data/csv/ripe_atlas/nodes.csv"),
        "edges": Path("data/csv/ripe_atlas/edges.csv"),
    },
}

graph_type = st.selectbox("Selecciona topología", GRAPH_PATHS.keys())
paths = GRAPH_PATHS[graph_type]

# --------------------------------------------------
# Cargar grafo
# --------------------------------------------------
with st.spinner("Cargando grafo..."):
    g, node_metadata = load_graph_from_csv(
        nodes_csv_path=paths["nodes"],
        edges_csv_path=paths["edges"]
    )

st.success("Grafo cargado correctamente")

# ==================================================
# 1️⃣ Métricas globales
# ==================================================
st.header("📊 Métricas globales")

stats = graph_basic_stats(g)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ASNs", stats["nodes"])
c2.metric("Aristas", stats["edges"])
c3.metric("In-degree promedio", f"{stats['avg_in_degree']:.2f}")
c4.metric("Out-degree promedio", f"{stats['avg_out_degree']:.2f}")
c5.metric("Grado máximo", stats["max_degree"])

st.write("**Tipo de grafo:** Dirigido (AS → AS)")

# ==================================================
# 2️⃣ Distribución de grado
# ==================================================
st.header("📈 Distribución de grado")

deg = (g.in_degrees() + g.out_degrees()).numpy()
deg_df = pd.DataFrame({"degree": deg})

st.bar_chart(deg_df["degree"].value_counts().sort_index())

# ==================================================
# 3️⃣ Top-K ASNs
# ==================================================
st.header("🏆 ASNs más conectados")

k = st.slider("Top-K", 5, 50, 10)
topk_df = top_k_nodes_by_degree(g, node_metadata, k)

st.dataframe(topk_df, use_container_width=True)

# ==================================================
# 4️⃣ Exploración local (subgrafo)
# ==================================================
st.header("🔍 Exploración local por ASN")

asn_input = st.number_input(
    "ASN central",
    min_value=1,
    step=1
)

hops = st.slider("Hops (ego-network)", 1, 3, 1)

if st.button("Construir subgrafo"):
    subg, center = ego_subgraph_by_asn(g, asn_input, hops)

    if subg is None:
        st.warning("ASN no encontrado en el grafo")
    else:
        st.success("Subgrafo construido")

        asn = int(g.ndata["asn"][center])
        name = node_metadata["name"].get(center, "Nombre no disponible")

        c1, c2, c3 = st.columns(3)
        c1.metric("Nodos", subg.num_nodes())
        c2.metric("Aristas", subg.num_edges())
        c3.metric(
            "Grado ASN",
            int(g.in_degrees()[center] + g.out_degrees()[center])
        )

        st.markdown(
            f"""
            **ASN central:** AS{asn}  
            **Nombre:** {name}  
            **In-degree:** {int(g.in_degrees()[center])}  
            **Out-degree:** {int(g.out_degrees()[center])}  
            """
        )

        if "path_occurrences" in g.ndata:
            st.write(
                f"**Path occurrences:** {int(g.ndata['path_occurrences'][center])}"
            )

        with st.expander("ASNs en el subgrafo"):
            st.write(
                sorted(subg.ndata["asn"].numpy().tolist())
            )
