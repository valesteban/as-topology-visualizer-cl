"""
Módulo de visualizaciones académicas para análisis de topologías AS-level.
Incluye gráficos con estilo científico y configuraciones optimizadas para publicación.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import io
import base64
import dgl
import networkx as nx
from pyvis.network import Network


# Paleta de colores académica consistente
COLORS = {
    "BGP": "#2E86AB",           # Azul oscuro - Control plane
    "RIPE Atlas": "#A23B72",     # Púrpura - Data plane
    "Merged": "#F18F01",         # Naranja - Combinado
    "Overlap": "#C73E1D",        # Rojo - Intersección
    "Exclusive BGP": "#6A8EAE",  # Azul claro
    "Exclusive RIPE": "#C17C9F", # Púrpura claro
}


def _select_top_nodes_by_degree(g, max_nodes=300):
    """Selecciona los nodos con mayor grado total para submuestrear grafos grandes."""
    num_nodes = g.num_nodes()
    if max_nodes is None or max_nodes >= num_nodes:
        return list(range(num_nodes))

    degrees = (g.in_degrees() + g.out_degrees()).numpy()
    top_indices = np.argsort(degrees)[-max_nodes:]
    return top_indices.tolist()


def build_pyvis_network(
    g,
    node_metadata=None,
    title="AS Topology",
    max_nodes=300,
    max_edges=2000,
    height="650px",
    width="100%",
    seed=42,
):
    """
    Genera un grafo interactivo con PyVis para exploración rápida.

    Retorna:
        html (str): HTML embebible para Streamlit.
    """
    node_metadata = node_metadata or {}
    name_map = node_metadata.get("name", {})

    selected_nodes = _select_top_nodes_by_degree(g, max_nodes=max_nodes)
    g_sub = dgl.node_subgraph(g, selected_nodes)

    src, dst = g_sub.edges()
    edge_list = list(zip(src.tolist(), dst.tolist()))

    if max_edges is not None and len(edge_list) > max_edges:
        rng = np.random.default_rng(seed)
        edge_indices = rng.choice(len(edge_list), size=max_edges, replace=False)
        edge_list = [edge_list[i] for i in edge_indices]

    degrees = (g_sub.in_degrees() + g_sub.out_degrees()).numpy()
    asn_values = g_sub.ndata.get("asn")

    net = Network(height=height, width=width, bgcolor="#ffffff", font_color="#1f2937")
    net.force_atlas_2based(gravity=-50, spring_length=100, spring_strength=0.08, damping=0.4)

    for node_id in range(g_sub.num_nodes()):
        asn = int(asn_values[node_id]) if asn_values is not None else int(node_id)
        label = f"AS{asn}"
        tooltip_name = name_map.get(int(selected_nodes[node_id]), "")
        title_text = f"{label}<br>{tooltip_name}" if tooltip_name else label
        size = max(6, min(30, int(degrees[node_id]) + 4))

        net.add_node(
            node_id,
            label=label,
            title=title_text,
            size=size,
            color="#3b82f6" if degrees[node_id] > 5 else "#93c5fd",
        )

    for src_id, dst_id in edge_list:
        net.add_edge(src_id, dst_id)

    net.set_options("""
    var options = {
      "nodes": {
        "borderWidth": 1,
        "borderWidthSelected": 2
      },
      "edges": {
        "color": {"inherit": true},
        "smooth": {"type": "dynamic"}
      },
      "physics": {
        "stabilization": {"iterations": 200}
      }
    }
    """)

    html = net.generate_html(notebook=False)
    return html


def plot_k_core_profile(g, max_nodes=2000, title="Perfil de K-Core"):
    """Distribución de tamaños de k-cores para explorar estructura núcleo-periferia."""
    selected_nodes = _select_top_nodes_by_degree(g, max_nodes=max_nodes)
    g_sub = dgl.node_subgraph(g, selected_nodes)

    nx_graph = dgl.to_networkx(g_sub).to_undirected()
    if nx_graph.number_of_nodes() == 0:
        return go.Figure()

    core_numbers = nx.core_number(nx_graph)
    core_counts = pd.Series(core_numbers).value_counts().sort_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=core_counts.index.astype(int),
        y=core_counts.values,
        marker_color="#0ea5e9",
    ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        xaxis_title="k-core",
        yaxis_title="Número de ASNs",
        plot_bgcolor="white",
        yaxis=dict(gridcolor="lightgray"),
    )
    return fig


def plot_neighbor_degree_correlation(
    g,
    max_nodes=2000,
    title="Grado vs Grado Promedio de Vecinos",
):
    """Scatter del grado vs grado promedio de vecinos para estudiar interconexión."""
    selected_nodes = _select_top_nodes_by_degree(g, max_nodes=max_nodes)
    g_sub = dgl.node_subgraph(g, selected_nodes)
    nx_graph = dgl.to_networkx(g_sub).to_undirected()

    if nx_graph.number_of_nodes() == 0:
        return go.Figure()

    degree_dict = dict(nx_graph.degree())
    neighbor_degree = nx.average_neighbor_degree(nx_graph)

    degrees = [degree_dict[n] for n in nx_graph.nodes()]
    neighbor_avg = [neighbor_degree[n] for n in nx_graph.nodes()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=degrees,
        y=neighbor_avg,
        mode="markers",
        marker=dict(size=7, color="#f97316", opacity=0.7),
        text=[f"Nodo {n}" for n in nx_graph.nodes()],
    ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        xaxis_title="Grado del ASN",
        yaxis_title="Grado promedio de vecinos",
        plot_bgcolor="white",
        xaxis=dict(gridcolor="lightgray"),
        yaxis=dict(gridcolor="lightgray"),
    )
    return fig


def plot_degree_distribution_loglog(g, title="Degree Distribution", color=COLORS["BGP"]):
    """
    Distribución de grado en escala log-log.
    Apropiada para identificar power-law behavior típico de topologías AS-level.
    """
    degrees = (g.in_degrees() + g.out_degrees()).numpy()
    
    # Calcular distribución
    unique_degrees, counts = np.unique(degrees, return_counts=True)
    
    # Filtrar grado 0 para log-log
    mask = unique_degrees > 0
    unique_degrees = unique_degrees[mask]
    counts = counts[mask]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=unique_degrees,
        y=counts,
        mode='markers',
        marker=dict(size=8, color=color, opacity=0.6),
        name='Observed'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16)),
        xaxis=dict(
            title="Degree (k)",
            type="log",
            gridcolor='lightgray',
            showgrid=True
        ),
        yaxis=dict(
            title="Frequency P(k)",
            type="log",
            gridcolor='lightgray',
            showgrid=True
        ),
        plot_bgcolor='white',
        hovermode='closest',
        showlegend=False
    )
    
    return fig


def plot_in_out_degree_comparison(g, title="In-Degree vs Out-Degree Distribution"):
    """
    Comparación entre in-degree y out-degree para analizar asimetría
    en relaciones provider-customer.
    """
    in_degrees = g.in_degrees().numpy()
    out_degrees = g.out_degrees().numpy()
    
    # Distribuciones
    in_unique, in_counts = np.unique(in_degrees[in_degrees > 0], return_counts=True)
    out_unique, out_counts = np.unique(out_degrees[out_degrees > 0], return_counts=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=in_unique,
        y=in_counts,
        mode='markers+lines',
        marker=dict(size=6, color=COLORS["BGP"]),
        line=dict(width=1, color=COLORS["BGP"]),
        name='In-degree (customers)'
    ))
    
    fig.add_trace(go.Scatter(
        x=out_unique,
        y=out_counts,
        mode='markers+lines',
        marker=dict(size=6, color=COLORS["RIPE Atlas"]),
        line=dict(width=1, color=COLORS["RIPE Atlas"]),
        name='Out-degree (providers)'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16)),
        xaxis=dict(title="Degree", type="log", gridcolor='lightgray'),
        yaxis=dict(title="Frequency", type="log", gridcolor='lightgray'),
        plot_bgcolor='white',
        hovermode='closest',
        legend=dict(x=0.7, y=0.95, bgcolor='rgba(255,255,255,0.8)')
    )
    
    return fig


def plot_three_graph_comparison(graphs_dict):
    """
    Comparación de distribuciones de grado entre BGP, RIPE Atlas y Merged.
    """
    fig = go.Figure()
    
    for name, g in graphs_dict.items():
        degrees = (g.in_degrees() + g.out_degrees()).numpy()
        unique_degrees, counts = np.unique(degrees[degrees > 0], return_counts=True)
        
        fig.add_trace(go.Scatter(
            x=unique_degrees,
            y=counts,
            mode='markers+lines',
            marker=dict(size=6, color=COLORS.get(name, "#666666")),
            line=dict(width=1.5),
            name=name
        ))
    
    fig.update_layout(
        title=dict(
            text="Degree Distribution Comparison: Control-Plane vs Data-Plane",
            x=0.5,
            xanchor='center',
            font=dict(size=16)
        ),
        xaxis=dict(
            title="Degree (k)",
            type="log",
            gridcolor='lightgray',
            showgrid=True
        ),
        yaxis=dict(
            title="Frequency P(k)",
            type="log",
            gridcolor='lightgray',
            showgrid=True
        ),
        plot_bgcolor='white',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='gray',
            borderwidth=1
        )
    )
    
    return fig


def plot_asn_overlap_venn(g_bgp, g_ripe):
    """
    Visualización de overlap de ASNs entre BGP y RIPE Atlas.
    """
    asns_bgp = set(g_bgp.ndata["asn"].numpy())
    asns_ripe = set(g_ripe.ndata["asn"].numpy())
    
    only_bgp = len(asns_bgp - asns_ripe)
    only_ripe = len(asns_ripe - asns_bgp)
    both = len(asns_bgp & asns_ripe)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Only BGP', 'Overlap', 'Only RIPE'],
        y=[only_bgp, both, only_ripe],
        marker=dict(color=[
            COLORS["Exclusive BGP"],
            COLORS["Overlap"],
            COLORS["Exclusive RIPE"]
        ]),
        text=[only_bgp, both, only_ripe],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=dict(
            text=f"ASN Overlap Analysis (Total: {len(asns_bgp | asns_ripe)} unique ASNs)",
            x=0.5,
            xanchor='center',
            font=dict(size=16)
        ),
        yaxis=dict(title="Number of ASNs", gridcolor='lightgray'),
        plot_bgcolor='white',
        showlegend=False
    )
    
    return fig


def plot_degree_correlation(g_bgp, g_ripe):
    """
    Correlación de grado entre BGP y RIPE Atlas para ASNs comunes.
    Permite identificar ASNs con alta visibilidad en control-plane pero baja en data-plane.
    """
    asns_bgp = g_bgp.ndata["asn"].numpy()
    asns_ripe = g_ripe.ndata["asn"].numpy()
    
    # Mapear ASN -> degree
    degree_bgp_dict = {
        int(asns_bgp[i]): int((g_bgp.in_degrees() + g_bgp.out_degrees())[i])
        for i in range(g_bgp.num_nodes())
    }
    
    degree_ripe_dict = {
        int(asns_ripe[i]): int((g_ripe.in_degrees() + g_ripe.out_degrees())[i])
        for i in range(g_ripe.num_nodes())
    }
    
    # ASNs comunes
    common_asns = set(degree_bgp_dict.keys()) & set(degree_ripe_dict.keys())
    
    bgp_degrees = [degree_bgp_dict[asn] for asn in common_asns]
    ripe_degrees = [degree_ripe_dict[asn] for asn in common_asns]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=bgp_degrees,
        y=ripe_degrees,
        mode='markers',
        marker=dict(
            size=8,
            color=COLORS["Overlap"],
            opacity=0.5,
            line=dict(width=0.5, color='white')
        ),
        text=[f"ASN: {asn}" for asn in common_asns],
        hovertemplate='<b>%{text}</b><br>BGP Degree: %{x}<br>RIPE Degree: %{y}<extra></extra>'
    ))
    
    # Línea de referencia y=x
    max_val = max(max(bgp_degrees) if bgp_degrees else 1, 
                  max(ripe_degrees) if ripe_degrees else 1)
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode='lines',
        line=dict(color='gray', dash='dash', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Calcular correlación
    if len(bgp_degrees) > 1:
        correlation = np.corrcoef(bgp_degrees, ripe_degrees)[0, 1]
        corr_text = f"Pearson r = {correlation:.3f}"
    else:
        corr_text = "N/A"
    
    fig.update_layout(
        title=dict(
            text=f"Degree Correlation: BGP vs RIPE Atlas ({len(common_asns)} common ASNs)<br><sub>{corr_text}</sub>",
            x=0.5,
            xanchor='center',
            font=dict(size=16)
        ),
        xaxis=dict(
            title="BGP Degree (Control-Plane)",
            type="log",
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title="RIPE Atlas Degree (Data-Plane)",
            type="log",
            gridcolor='lightgray'
        ),
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    return fig


def plot_path_occurrences_vs_degree(g, title="Path Occurrences vs Degree"):
    """
    Relación entre centralidad (path occurrences) y conectividad (degree).
    """
    if "path_occurrences" not in g.ndata:
        return None
    
    degrees = (g.in_degrees() + g.out_degrees()).numpy()
    paths = g.ndata["path_occurrences"].numpy()
    
    # Filtrar nodos con degree > 0
    mask = degrees > 0
    degrees = degrees[mask]
    paths = paths[mask]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=degrees,
        y=paths,
        mode='markers',
        marker=dict(
            size=6,
            color=COLORS["BGP"],
            opacity=0.4,
            line=dict(width=0.5, color='white')
        ),
        hovertemplate='Degree: %{x}<br>Path Occurrences: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16)),
        xaxis=dict(
            title="Degree",
            type="log",
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title="Path Occurrences (Centrality)",
            type="log",
            gridcolor='lightgray'
        ),
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    return fig


def plot_top_k_comparison(graphs_dict, k=20):
    """
    Comparación de top-K ASNs por grado entre diferentes grafos.
    Visualiza el overlap estructural en los nodos más centrales.
    """
    top_asns = {}
    
    for name, g in graphs_dict.items():
        degrees = (g.in_degrees() + g.out_degrees()).numpy()
        asns = g.ndata["asn"].numpy()
        
        # Top K por grado
        top_indices = np.argsort(degrees)[::-1][:k]
        top_asns[name] = set(int(asns[i]) for i in top_indices)
    
    # Calcular overlaps
    if "BGP" in top_asns and "RIPE Atlas" in top_asns:
        overlap = len(top_asns["BGP"] & top_asns["RIPE Atlas"])
        only_bgp = len(top_asns["BGP"] - top_asns["RIPE Atlas"])
        only_ripe = len(top_asns["RIPE Atlas"] - top_asns["BGP"])
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[f'Only BGP<br>Top-{k}', f'Overlap<br>Top-{k}', f'Only RIPE<br>Top-{k}'],
            y=[only_bgp, overlap, only_ripe],
            marker=dict(color=[
                COLORS["Exclusive BGP"],
                COLORS["Overlap"],
                COLORS["Exclusive RIPE"]
            ]),
            text=[only_bgp, overlap, only_ripe],
            textposition='auto',
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Top-{k} ASNs Overlap by Degree",
                x=0.5,
                xanchor='center',
                font=dict(size=16)
            ),
            yaxis=dict(title="Number of ASNs", gridcolor='lightgray'),
            plot_bgcolor='white',
            showlegend=False
        )
        
        return fig
    
    return None


def plot_metrics_comparison_table(stats_df):
    """
    Tabla visual comparativa de métricas entre grafos.
    """
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Metric</b>'] + [f'<b>{col}</b>' for col in stats_df.columns],
            fill_color='lightgray',
            align='left',
            font=dict(size=12, color='black')
        ),
        cells=dict(
            values=[stats_df.index] + [stats_df[col] for col in stats_df.columns],
            fill_color='white',
            align='left',
            font=dict(size=11)
        )
    )])
    
    fig.update_layout(
        title=dict(
            text="Comparative Graph Metrics: Control-Plane vs Data-Plane",
            x=0.5,
            xanchor='center',
            font=dict(size=16)
        ),
        height=400
    )
    
    return fig


def plot_venn_diagram_asn_overlap(g_bgp, g_ripe, g_merged=None):
    """
    Crea un diagrama de Venn profesional mostrando overlap de ASNs entre fuentes.
    Similar al estilo de la imagen proporcionada.
    
    Args:
        g_bgp: Grafo BGP
        g_ripe: Grafo RIPE Atlas (renombrado como Traceroute)
        g_merged: Grafo Merged opcional (renombrado como CAIDA)
    
    Returns:
        tuple: (fig_asn, fig_edges) - Figuras matplotlib para ASNs y aristas
    """
    asns_bgp = set(g_bgp.ndata["asn"].numpy())
    asns_traceroute = set(g_ripe.ndata["asn"].numpy())
    
    # Extraer aristas
    edges_bgp = set()
    src_bgp, dst_bgp = g_bgp.edges()
    for i in range(len(src_bgp)):
        u = int(g_bgp.ndata["asn"][src_bgp[i]])
        v = int(g_bgp.ndata["asn"][dst_bgp[i]])
        edges_bgp.add((min(u, v), max(u, v)))
    
    edges_traceroute = set()
    src_tr, dst_tr = g_ripe.edges()
    for i in range(len(src_tr)):
        u = int(g_ripe.ndata["asn"][src_tr[i]])
        v = int(g_ripe.ndata["asn"][dst_tr[i]])
        edges_traceroute.add((min(u, v), max(u, v)))
    
    if g_merged is not None:
        asns_caida = set(g_merged.ndata["asn"].numpy())
        
        edges_caida = set()
        src_m, dst_m = g_merged.edges()
        for i in range(len(src_m)):
            u = int(g_merged.ndata["asn"][src_m[i]])
            v = int(g_merged.ndata["asn"][dst_m[i]])
            edges_caida.add((min(u, v), max(u, v)))
        
        # Diagrama de Venn de 3 conjuntos (ASNs)
        fig_asn, ax_asn = plt.subplots(figsize=(10, 8))
        venn_asn = venn3(
            [asns_bgp, asns_traceroute, asns_caida],
            set_labels=('BGP', 'Traceroute', 'CAIDA'),
            set_colors=('#9999FF', '#FF99CC', '#99CCFF'),  # Colores suaves
            alpha=0.5,
            ax=ax_asn
        )
        
        # Personalizar estilo
        for text in venn_asn.set_labels:
            if text:
                text.set_fontsize(14)
                text.set_fontweight('bold')
        
        for text in venn_asn.subset_labels:
            if text:
                text.set_fontsize(12)
        
        ax_asn.set_title('Overlap de ASNs entre las 3 fuentes', fontsize=16, fontweight='bold', pad=20)
        
        # Diagrama de Venn de 3 conjuntos (Aristas)
        fig_edges, ax_edges = plt.subplots(figsize=(10, 8))
        venn_edges = venn3(
            [edges_bgp, edges_traceroute, edges_caida],
            set_labels=('BGP', 'Traceroute', 'CAIDA'),
            set_colors=('#9999FF', '#FF99CC', '#99CCFF'),
            alpha=0.5,
            ax=ax_edges
        )
        
        for text in venn_edges.set_labels:
            if text:
                text.set_fontsize(14)
                text.set_fontweight('bold')
        
        for text in venn_edges.subset_labels:
            if text:
                text.set_fontsize(12)
        
        ax_edges.set_title('Overlap de Aristas entre las 3 fuentes', fontsize=16, fontweight='bold', pad=20)
        
    else:
        # Diagrama de Venn de 2 conjuntos (ASNs)
        fig_asn, ax_asn = plt.subplots(figsize=(10, 8))
        venn_asn = venn2(
            [asns_bgp, asns_traceroute],
            set_labels=('BGP', 'Traceroute'),
            set_colors=('#9999FF', '#FF99CC'),
            alpha=0.5,
            ax=ax_asn
        )
        
        for text in venn_asn.set_labels:
            if text:
                text.set_fontsize(14)
                text.set_fontweight('bold')
        
        for text in venn_asn.subset_labels:
            if text:
                text.set_fontsize(12)
        
        ax_asn.set_title('Overlap de ASNs entre las 2 fuentes', fontsize=16, fontweight='bold', pad=20)
        
        # Diagrama de Venn de 2 conjuntos (Aristas)
        fig_edges, ax_edges = plt.subplots(figsize=(10, 8))
        venn_edges = venn2(
            [edges_bgp, edges_traceroute],
            set_labels=('BGP', 'Traceroute'),
            set_colors=('#9999FF', '#FF99CC'),
            alpha=0.5,
            ax=ax_edges
        )
        
        for text in venn_edges.set_labels:
            if text:
                text.set_fontsize(14)
                text.set_fontweight('bold')
        
        for text in venn_edges.subset_labels:
            if text:
                text.set_fontsize(12)
        
        ax_edges.set_title('Overlap de Aristas entre las 2 fuentes', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    return fig_asn, fig_edges


def plot_venn_diagram_plotly(g_bgp, g_ripe, g_merged=None):
    """
    Versión alternativa usando Plotly para crear diagramas de Venn interactivos.
    Crea círculos manualmente con shapes de Plotly.
    
    Returns:
        tuple: (fig_asn, fig_edges) - Figuras Plotly para ASNs y aristas
    """
    asns_bgp = set(g_bgp.ndata["asn"].numpy())
    asns_traceroute = set(g_ripe.ndata["asn"].numpy())
    
    # Calcular overlaps
    only_bgp = len(asns_bgp - asns_traceroute)
    only_traceroute = len(asns_traceroute - asns_bgp)
    overlap_asn = len(asns_bgp & asns_traceroute)
    
    # Extraer aristas
    edges_bgp = set()
    src_bgp, dst_bgp = g_bgp.edges()
    for i in range(len(src_bgp)):
        u = int(g_bgp.ndata["asn"][src_bgp[i]])
        v = int(g_bgp.ndata["asn"][dst_bgp[i]])
        edges_bgp.add((min(u, v), max(u, v)))
    
    edges_traceroute = set()
    src_tr, dst_tr = g_ripe.edges()
    for i in range(len(src_tr)):
        u = int(g_ripe.ndata["asn"][src_tr[i]])
        v = int(g_ripe.ndata["asn"][dst_tr[i]])
        edges_traceroute.add((min(u, v), max(u, v)))
    
    only_bgp_edges = len(edges_bgp - edges_traceroute)
    only_traceroute_edges = len(edges_traceroute - edges_bgp)
    overlap_edges = len(edges_bgp & edges_traceroute)
    
    if g_merged is not None:
        asns_caida = set(g_merged.ndata["asn"].numpy())
        
        # Para 3 conjuntos, crear visualización con círculos
        fig_asn = go.Figure()
        
        # Círculo BGP (azul, izquierda)
        fig_asn.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=-1.5, y0=-1, x1=1.5, y1=2,
            line_color="#9999FF",
            fillcolor="#9999FF",
            opacity=0.3,
            layer="below"
        )
        
        # Círculo Traceroute (rosa, derecha)
        fig_asn.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=0, y0=-1, x1=3, y1=2,
            line_color="#FF99CC",
            fillcolor="#FF99CC",
            opacity=0.3,
            layer="below"
        )
        
        # Círculo CAIDA (azul claro, abajo)
        fig_asn.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=-0.75, y0=-2.5, x1=2.25, y1=0.5,
            line_color="#99CCFF",
            fillcolor="#99CCFF",
            opacity=0.3,
            layer="below"
        )
        
        # Etiquetas de conjuntos
        fig_asn.add_annotation(x=-1.2, y=2.3, text="BGP", showarrow=False, 
                              font=dict(size=16, color="black", family="Arial Black"))
        fig_asn.add_annotation(x=2.7, y=2.3, text="Traceroute", showarrow=False,
                              font=dict(size=16, color="black", family="Arial Black"))
        fig_asn.add_annotation(x=0.75, y=-2.8, text="CAIDA", showarrow=False,
                              font=dict(size=16, color="black", family="Arial Black"))
        
        # Números (aproximados para visualización)
        fig_asn.add_annotation(x=-0.9, y=0.8, text=str(only_bgp), showarrow=False, font=dict(size=14))
        fig_asn.add_annotation(x=2.4, y=0.8, text=str(only_traceroute), showarrow=False, font=dict(size=14))
        fig_asn.add_annotation(x=0.75, y=-1.5, text=str(len(asns_caida - asns_bgp - asns_traceroute)), 
                              showarrow=False, font=dict(size=14))
        fig_asn.add_annotation(x=0.75, y=0.5, text=str(overlap_asn), showarrow=False, font=dict(size=14))
        
        fig_asn.update_layout(
            title="Overlap de ASNs entre las 3 fuentes",
            xaxis=dict(range=[-2.5, 4], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[-3.5, 3], showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='white',
            height=600,
            width=800
        )
        
        # Similar para aristas
        fig_edges = go.Figure()
        
        fig_edges.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=-1.5, y0=-1, x1=1.5, y1=2,
            line_color="#9999FF",
            fillcolor="#9999FF",
            opacity=0.3,
            layer="below"
        )
        
        fig_edges.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=0, y0=-1, x1=3, y1=2,
            line_color="#FF99CC",
            fillcolor="#FF99CC",
            opacity=0.3,
            layer="below"
        )
        
        fig_edges.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=-0.75, y0=-2.5, x1=2.25, y1=0.5,
            line_color="#99CCFF",
            fillcolor="#99CCFF",
            opacity=0.3,
            layer="below"
        )
        
        fig_edges.add_annotation(x=-1.2, y=2.3, text="BGP", showarrow=False,
                                font=dict(size=16, color="black", family="Arial Black"))
        fig_edges.add_annotation(x=2.7, y=2.3, text="Traceroute", showarrow=False,
                                font=dict(size=16, color="black", family="Arial Black"))
        fig_edges.add_annotation(x=0.75, y=-2.8, text="CAIDA", showarrow=False,
                                font=dict(size=16, color="black", family="Arial Black"))
        
        fig_edges.add_annotation(x=-0.9, y=0.8, text=str(only_bgp_edges), showarrow=False, font=dict(size=14))
        fig_edges.add_annotation(x=2.4, y=0.8, text=str(only_traceroute_edges), showarrow=False, font=dict(size=14))
        fig_edges.add_annotation(x=0.75, y=0.5, text=str(overlap_edges), showarrow=False, font=dict(size=14))
        
        fig_edges.update_layout(
            title="Overlap de Aristas entre las 3 fuentes",
            xaxis=dict(range=[-2.5, 4], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[-3.5, 3], showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='white',
            height=600,
            width=800
        )
        
    else:
        # Diagrama de 2 conjuntos (más simple)
        fig_asn = go.Figure()
        
        # Círculo BGP (azul, izquierda)
        fig_asn.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=-1, y0=-1, x1=1, y1=1,
            line_color="#9999FF",
            fillcolor="#9999FF",
            opacity=0.4,
            layer="below"
        )
        
        # Círculo Traceroute (rosa, derecha)
        fig_asn.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=0, y0=-1, x1=2, y1=1,
            line_color="#FF99CC",
            fillcolor="#FF99CC",
            opacity=0.4,
            layer="below"
        )
        
        # Etiquetas
        fig_asn.add_annotation(x=-0.5, y=1.3, text="BGP", showarrow=False,
                              font=dict(size=16, color="black", family="Arial Black"))
        fig_asn.add_annotation(x=1.5, y=1.3, text="Traceroute", showarrow=False,
                              font=dict(size=16, color="black", family="Arial Black"))
        
        # Números
        fig_asn.add_annotation(x=-0.5, y=0, text=str(only_bgp), showarrow=False, font=dict(size=14))
        fig_asn.add_annotation(x=0.5, y=0, text=str(overlap_asn), showarrow=False, font=dict(size=14))
        fig_asn.add_annotation(x=1.5, y=0, text=str(only_traceroute), showarrow=False, font=dict(size=14))
        
        fig_asn.update_layout(
            title="Overlap de ASNs entre las 2 fuentes",
            xaxis=dict(range=[-1.5, 2.5], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[-1.5, 1.8], showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='white',
            height=500,
            width=700
        )
        
        # Aristas
        fig_edges = go.Figure()
        
        fig_edges.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=-1, y0=-1, x1=1, y1=1,
            line_color="#9999FF",
            fillcolor="#9999FF",
            opacity=0.4,
            layer="below"
        )
        
        fig_edges.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=0, y0=-1, x1=2, y1=1,
            line_color="#FF99CC",
            fillcolor="#FF99CC",
            opacity=0.4,
            layer="below"
        )
        
        fig_edges.add_annotation(x=-0.5, y=1.3, text="BGP", showarrow=False,
                                font=dict(size=16, color="black", family="Arial Black"))
        fig_edges.add_annotation(x=1.5, y=1.3, text="Traceroute", showarrow=False,
                                font=dict(size=16, color="black", family="Arial Black"))
        
        fig_edges.add_annotation(x=-0.5, y=0, text=str(only_bgp_edges), showarrow=False, font=dict(size=14))
        fig_edges.add_annotation(x=0.5, y=0, text=str(overlap_edges), showarrow=False, font=dict(size=14))
        fig_edges.add_annotation(x=1.5, y=0, text=str(only_traceroute_edges), showarrow=False, font=dict(size=14))
        
        fig_edges.update_layout(
            title="Overlap de Aristas entre las 2 fuentes",
            xaxis=dict(range=[-1.5, 2.5], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[-1.5, 1.8], showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='white',
            height=500,
            width=700
        )
    
    return fig_asn, fig_edges
