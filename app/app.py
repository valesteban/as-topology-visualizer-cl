import sys
from pathlib import Path

# ==================================================
# PYTHONPATH
# ==================================================
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st
from pathlib import Path

from src.load_csv_graph import load_graph_from_csv
from src.stats import graph_basic_stats
from src.tables import (
    full_node_table,
    top_k_by_path_occurrences,
    critical_asn_score
)
from src.plots import degree_vs_paths, path_occurrences_histogram
from src.compare import compare_graphs


st.set_page_config(page_title="AS Topology Visualizer", layout="wide")
st.title("🌐 AS Topology Visualizer — Chile")

GRAPH_PATHS = {
    "BGP": "data/csv/bgp",
    "RIPE Atlas": "data/csv/ripe_atlas",
    "Merged": "data/csv/merged",
}

graph_name = st.selectbox("Selecciona topología", GRAPH_PATHS.keys())
base = Path(GRAPH_PATHS[graph_name])

g, node_metadata = load_graph_from_csv(
    base / "nodes.csv",
    base / "edges.csv"
)

# -------------------------
# Métricas globales
# -------------------------
st.header("📊 Métricas globales")
stats = graph_basic_stats(g)
st.write(stats)

# -------------------------
# Tabla de nodos
# -------------------------
st.header("📋 ASNs")
st.dataframe(full_node_table(g, node_metadata), height=400)

# -------------------------
# Top-K
# -------------------------
st.header("🔝 Top ASNs por Path Occurrences")
k = st.slider("Top-K", 5, 50, 20)
st.dataframe(top_k_by_path_occurrences(g, node_metadata, k))

# -------------------------
# Ranking crítico
# -------------------------
st.header("🔥 ASNs críticos")
st.dataframe(critical_asn_score(g, node_metadata).head(30))

# -------------------------
# Gráficos
# -------------------------
st.header("📈 Degree vs Path Occurrences")
st.scatter_chart(degree_vs_paths(g))

hist = path_occurrences_histogram(g)
if hist is not None:
    st.bar_chart(hist)
