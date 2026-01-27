# import sys
# from pathlib import Path
# import streamlit as st
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# # =====================================================
# # Paths e imports del proyecto
# # =====================================================
# ROOT_DIR = Path(__file__).resolve().parents[1]
# sys.path.append(str(ROOT_DIR))

# from src.io.load_csv_graph import load_graph_from_csv

# # =====================================================
# # Configuración Streamlit
# # =====================================================
# st.set_page_config(
#     page_title="AS Topology Visualizer - Chile",
#     layout="wide"
# )

# st.title("🌐 Topología AS-level — Chile")
# st.caption("Análisis individual de grafos construidos desde BGP y RIPE Atlas")

# # =====================================================
# # Grafos disponibles
# # =====================================================
# BASE = Path("data/csv")

# GRAPH_CONFIG = {
#     "BGP": {
#         "nodes": BASE / "bgp/nodes.csv",
#         "edges": BASE / "bgp/edges.csv",
#     },
#     "RIPE Atlas": {
#         "nodes": BASE / "ripe_atlas/nodes.csv",
#         "edges": BASE / "ripe_atlas/edges.csv",
#     },
#     "Mixto (BGP + RIPE)": {
#         "nodes": BASE / "merged/nodes.csv",
#         "edges": BASE / "merged/edges.csv",
#     }
# }

# # =====================================================
# # Selector de grafo
# # =====================================================
# graph_name = st.selectbox(
#     "Selecciona la topología a analizar",
#     GRAPH_CONFIG.keys()
# )

# paths = GRAPH_CONFIG[graph_name]

# # =====================================================
# # Cargar grafo
# # =====================================================
# @st.cache_data(show_spinner=True)
# def load_graph(paths):
#     return load_graph_from_csv(
#         edges_csv=paths["edges"],
#         nodes_csv=paths["nodes"]
#     )

# try:
#     g = load_graph(paths)
# except Exception as e:
#     st.error(f"❌ Error cargando el grafo: {e}")
#     st.stop()

# # =====================================================
# # Funciones auxiliares
# # =====================================================
# def degree(g):
#     return g.in_degrees().numpy() + g.out_degrees().numpy()

# def reciprocity(g):
#     src, dst = g.edges()
#     edges = set(zip(src.tolist(), dst.tolist()))
#     rev = set(zip(dst.tolist(), src.tolist()))
#     return len(edges & rev) / len(edges) if edges else 0.0

# def top_asns(g, k):
#     return (
#         pd.DataFrame({
#             "ASN": g.ndata["asn"].numpy(),
#             "Grado": degree(g)
#         })
#         .sort_values("Grado", ascending=False)
#         .head(k)
#     )

# def subgraph_by_asn(g, target_asn):
#     asns = g.ndata["asn"].numpy()
#     idx = np.where(asns == target_asn)[0]

#     if len(idx) == 0:
#         return None

#     node_id = int(idx[0])
#     neighbors = (
#         g.successors(node_id).tolist()
#         + g.predecessors(node_id).tolist()
#     )
#     nodes = list(set(neighbors + [node_id]))

#     return g.subgraph(nodes)

# # =====================================================
# # Métricas generales
# # =====================================================
# st.header("📌 Métricas generales")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.metric("Nodos (ASNs)", g.num_nodes())

# with col2:
#     st.metric("Aristas", g.num_edges())

# with col3:
#     st.metric("Tipo de grafo", "Dirigido (AS-level)")

# # =====================================================
# # Distribución de grado
# # =====================================================
# st.header("📊 Distribución de grado")

# fig, ax = plt.subplots(figsize=(8, 5))
# ax.hist(degree(g), bins=50, log=True)
# ax.set_xlabel("Grado total")
# ax.set_ylabel("Frecuencia (log)")
# ax.set_title("Distribución de grado AS-level")

# st.pyplot(fig)

# st.markdown("""
# Esta distribución muestra una **cola larga**, típica de redes AS-level:
# pocos ASNs altamente conectados y muchos ASNs con baja conectividad.
# """)

# # =====================================================
# # Top ASNs por grado
# # =====================================================
# st.header("🏆 Top ASNs por grado")

# top_k = st.slider("Top K", 5, 50, 10, step=5)
# st.dataframe(top_asns(g, top_k))

# # =====================================================
# # Reciprocidad
# # =====================================================
# st.header("🔁 Reciprocidad de enlaces")

# rec = reciprocity(g)
# st.metric("Proporción de aristas recíprocas", f"{rec:.2%}")

# st.markdown("""
# Una mayor reciprocidad suele indicar rutas observadas
# en ambos sentidos (común en mediciones RIPE Atlas).
# """)

# # =====================================================
# # Peso total de aristas
# # =====================================================
# if "weight" in g.edata:
#     st.header("⚖️ Uso observado (peso de aristas)")
#     st.metric("Suma total de pesos", int(g.edata["weight"].sum()))

# # =====================================================
# # Exploración local por ASN
# # =====================================================
# st.header("🔍 Exploración local por ASN")

# asn_input = st.number_input(
#     "Ingresa un ASN para explorar su vecindad",
#     min_value=1,
#     step=1
# )

# if st.button("Construir subgrafo"):
#     sg = subgraph_by_asn(g, asn_input)

#     if sg is None:
#         st.warning("ASN no encontrado en el grafo")
#     else:
#         st.success("Subgrafo construido")
#         col1, col2 = st.columns(2)
#         col1.metric("Nodos en subgrafo", sg.num_nodes())
#         col2.metric("Aristas en subgrafo", sg.num_edges())

# # =====================================================
# # Vista previa
# # =====================================================
# st.header("👀 Vista previa de ASNs")

# st.write("Primeros 30 ASNs del grafo:")
# st.write(g.ndata["asn"][:30].tolist())


















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
