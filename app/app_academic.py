"""
AS Topology Visualizer - Chile
Análisis Académico de Topologías AS-Level: Control-Plane vs Data-Plane

Esta aplicación proporciona un análisis comprehensivo de las topologías de Internet
a nivel de Sistemas Autónomos (AS) para Chile, comparando tres perspectivas:
- BGP (Control-Plane): Routing announcements
- RIPE Atlas (Data-Plane): Active measurements (traceroute)
- Merged: Hybrid view combining both sources
"""

import sys
from pathlib import Path

# ==================================================
# PYTHONPATH Setup
# ==================================================
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# ==================================================
# Imports
# ==================================================
import streamlit as st
import pandas as pd

from src.load_csv_graph import load_graph_from_csv
from src.analysis import (
    compute_advanced_metrics,
    compare_graph_metrics,
    compute_asn_overlap_metrics,
    analyze_degree_distribution,
    identify_critical_asns,
    analyze_hierarchical_structure,
    compute_edge_overlap,
    generate_academic_summary
)
from src.visualizations import (
    plot_degree_distribution_loglog,
    plot_in_out_degree_comparison,
    plot_three_graph_comparison,
    plot_asn_overlap_venn,
    plot_degree_correlation,
    plot_path_occurrences_vs_degree,
    plot_top_k_comparison,
    plot_venn_diagram_asn_overlap,
    plot_venn_diagram_plotly,
    COLORS
)
from src.interpretations import get_academic_context

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="AS Topology Analyzer - Chile",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# Custom CSS for Academic Style
# ==================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #0f172a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .interpretation-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f1f5f9;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# Title and Introduction
# ==================================================
st.markdown('<div class="main-header">🌐 AS Topology Analyzer — Chile</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Análisis Académico de Topologías AS-Level: Control-Plane vs Data-Plane</div>', unsafe_allow_html=True)

# ==================================================
# Sidebar: Configuration and Information
# ==================================================
with st.sidebar:
    st.header("⚙️ Configuración")
    
    st.markdown("""
    **Fuentes de Datos:**
    - **BGP**: RouteViews/RIS routing tables
    - **RIPE Atlas**: Traceroute measurements
    - **Merged**: Combined topology
    
    **Filtro**: Topología centrada en Chile
    """)
    
    st.divider()
    
    analysis_mode = st.radio(
        "Modo de Análisis",
        ["🔬 Comparativo Completo", "📊 Individual por Grafo", "🎯 Análisis Individual de ASNs"],
        help="Selecciona el tipo de análisis que deseas realizar"
    )
    
    st.divider()
    
    st.markdown("""
    **Glosario:**
    - **AS**: Autonomous System
    - **Control-Plane**: BGP routing
    - **Data-Plane**: Active traffic
    - **Stub AS**: Edge network
    - **Transit AS**: Intermediate provider
    - **Tier-1**: Top-level ISP
    """)

# ==================================================
# Load All Graphs
# ==================================================
@st.cache_data
def load_all_graphs():
    """Load all three graph topologies."""
    graphs = {}
    metadatas = {}
    
    graph_paths = {
        "BGP": Path("data/csv/bgp"),
        "RIPE Atlas": Path("data/csv/ripe_atlas"),
        "Merged": Path("data/csv/merged"),
    }
    
    for name, base_path in graph_paths.items():
        try:
            g, meta = load_graph_from_csv(
                base_path / "nodes.csv",
                base_path / "edges.csv"
            )
            graphs[name] = g
            metadatas[name] = meta
        except Exception as e:
            st.sidebar.error(f"Error cargando {name}: {e}")
    
    return graphs, metadatas

with st.spinner("🔄 Cargando topologías AS-level..."):
    graphs, metadatas = load_all_graphs()

if not graphs:
    st.error("❌ No se pudieron cargar los grafos. Verifica la estructura de datos.")
    st.stop()

st.sidebar.success(f"✅ {len(graphs)} grafos cargados exitosamente")

# ==================================================
# MAIN CONTENT
# ==================================================

if analysis_mode == "🔬 Comparativo Completo":
    # ============================================
    # SECTION 1: Executive Summary
    # ============================================
    st.markdown('<div class="section-header">📋 1. Resumen </div>', unsafe_allow_html=True)
    
    st.markdown("""
    Este análisis compara tres perspectivas de la topología de Internet en Chile a nivel AS-level:
    **BGP (control-plane)**, **RIPE Atlas (data-plane)**, y **Merged (híbrido)**. 
    """)
    
    # Comparative Metrics Table
    st.subheader("📊 Métricas Comparativas Globales")
    
    metrics_df = compare_graph_metrics(graphs)
    st.dataframe(metrics_df, use_container_width=True)
    
    # Key Insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bgp_nodes = graphs["BGP"].num_nodes()
        st.metric("ASNs en BGP", f"{bgp_nodes:,}", help="Control-plane: Routing announcements")
    
    with col2:
        ripe_nodes = graphs["RIPE Atlas"].num_nodes()
        st.metric("ASNs en RIPE", f"{ripe_nodes:,}", help="Data-plane: Active measurements")
    
    with col3:
        merged_nodes = graphs["Merged"].num_nodes()
        st.metric("ASNs en Merged", f"{merged_nodes:,}", help="Hybrid: Combined view")
    
    # ============================================
    # SECTION 2: ASN and Edge Overlap Analysis
    # ============================================
    st.markdown('<div class="section-header">📊 2. Análisis de Overlap</div>', unsafe_allow_html=True)
    
    # Selector de tipo de visualización
    viz_type = st.radio(
        "Tipo de visualización:",
        ["📊 Diagrama de Venn", "📈 Gráfico de barras", "🔵 Diagrama de Venn interactivo"],
        horizontal=True
    )
    
    tab1, tab2 = st.tabs(["🔢 Overlap de ASNs", "🔗 Overlap de Aristas"])
    
    with tab1:
        st.subheader("Overlap de Sistemas Autónomos")
        
        # Visualization según selección
        if viz_type == "📊 Diagrama de Venn":
            try:
                # Verificar si hay 3 grafos
                if "Merged" in graphs:
                    fig_asn, fig_edges = plot_venn_diagram_asn_overlap(
                        graphs["BGP"], 
                        graphs["RIPE Atlas"], 
                        graphs["Merged"]
                    )
                else:
                    fig_asn, fig_edges = plot_venn_diagram_asn_overlap(
                        graphs["BGP"], 
                        graphs["RIPE Atlas"]
                    )
                
                # Mostrar figura matplotlib
                st.pyplot(fig_asn)
                
            except Exception as e:
                st.error(f"Error al generar diagrama de Venn: {e}")
                st.info("Mostrando visualización alternativa...")
                fig_asn_overlap = plot_asn_overlap_venn(graphs["BGP"], graphs["RIPE Atlas"])
                st.plotly_chart(fig_asn_overlap, use_container_width=True)
        
        elif viz_type == "🔵 Diagrama de Venn interactivo":
            if "Merged" in graphs:
                fig_asn, fig_edges = plot_venn_diagram_plotly(
                    graphs["BGP"], 
                    graphs["RIPE Atlas"], 
                    graphs["Merged"]
                )
            else:
                fig_asn, fig_edges = plot_venn_diagram_plotly(
                    graphs["BGP"], 
                    graphs["RIPE Atlas"]
                )
            
            st.plotly_chart(fig_asn, use_container_width=True)
        
        else:  # Gráfico de barras
            fig_asn_overlap = plot_asn_overlap_venn(graphs["BGP"], graphs["RIPE Atlas"])
            st.plotly_chart(fig_asn_overlap, use_container_width=True)
        
        # Metrics
        asn_overlap_metrics = compute_asn_overlap_metrics(graphs["BGP"], graphs["RIPE Atlas"])
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Métricas de Overlap:**")
            for key, value in asn_overlap_metrics.items():
                st.markdown(f"- **{key}**: {value}")
        
        with col2:
            # Interpretation
            st.markdown(get_academic_context("asn_overlap"))
    
    with tab2:
        st.subheader("Overlap de Conexiones AS-to-AS")
        
        # Mostrar diagrama de aristas según selección
        if viz_type == "📊 Diagrama de Venn":
            try:
                # Ya generamos las figuras arriba, solo necesitamos mostrar fig_edges
                if "Merged" in graphs:
                    _, fig_edges = plot_venn_diagram_asn_overlap(
                        graphs["BGP"], 
                        graphs["RIPE Atlas"], 
                        graphs["Merged"]
                    )
                else:
                    _, fig_edges = plot_venn_diagram_asn_overlap(
                        graphs["BGP"], 
                        graphs["RIPE Atlas"]
                    )
                
                st.pyplot(fig_edges)
                
            except Exception as e:
                st.error(f"Error al generar diagrama de Venn: {e}")
        
        elif viz_type == "🔵 Diagrama de Venn interactivo (Plotly)":
            if "Merged" in graphs:
                _, fig_edges = plot_venn_diagram_plotly(
                    graphs["BGP"], 
                    graphs["RIPE Atlas"], 
                    graphs["Merged"]
                )
            else:
                _, fig_edges = plot_venn_diagram_plotly(
                    graphs["BGP"], 
                    graphs["RIPE Atlas"]
                )
            
            st.plotly_chart(fig_edges, use_container_width=True)
        
        try:
            edge_overlap_metrics = compute_edge_overlap(graphs["BGP"], graphs["RIPE Atlas"])
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Aristas en BGP", f"{edge_overlap_metrics.get('Edges in BGP', 0):,}")
            
            with col2:
                st.metric("Aristas en RIPE", f"{edge_overlap_metrics.get('Edges in RIPE', 0):,}")
            
            with col3:
                overlap_val = edge_overlap_metrics.get('Overlap Edges', 0)
                jaccard_val = edge_overlap_metrics.get('Jaccard Index', '0.000')
                st.metric("Overlap", f"{overlap_val:,}", delta=jaccard_val)
            
            st.markdown("**Métricas Detalladas:**")
            st.json(edge_overlap_metrics)
            
            st.info("""
            **Interpretación**: El overlap de aristas es menor que el overlap de ASNs, 
            ya que BGP captura muchas relaciones potenciales mientras RIPE solo observa rutas que realmente son utilizadas diariamente.
            """)
        
        except Exception as e:
            st.error(f"Error al calcular overlap de aristas: {e}")
            st.info("Por favor, recarga la aplicación o verifica que los datos estén correctos.")
            # Mostrar información de debug
            st.code(f"Grafos disponibles: {list(graphs.keys())}")
            import traceback
            st.code(traceback.format_exc())

    # Un Jaccard Index bajo es esperado y refleja la complementariedad de ambas fuentes.
    # ============================================
    # SECTION 3: Degree Distribution Analysis
    # ============================================
    st.markdown('<div class="section-header">📈 3. Análisis de Distribuciones de Grado</div>', unsafe_allow_html=True)
    
    st.markdown(get_academic_context("degree_distribution"))
    
    # Three-graph comparison
    st.subheader("Comparación de Distribuciones: BGP vs RIPE vs Merged")
    
    fig_comparison = plot_three_graph_comparison(graphs)
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Individual distributions
    tabs = st.tabs(["BGP (Control-Plane)", "RIPE Atlas (Data-Plane)", "Merged (Hybrid)"])
    
    for idx, (name, g) in enumerate(graphs.items()):
        with tabs[idx]:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = plot_degree_distribution_loglog(g, 
                    title=f"Degree Distribution: {name}",
                    color=COLORS[name])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Estadísticas de Distribución:**")
                dist_stats = analyze_degree_distribution(g)
                for key, value in dist_stats.items():
                    st.markdown(f"- **{key}**: {value}")
    
    # ============================================
    # SECTION 4: In-Degree vs Out-Degree
    # ============================================
    st.markdown('<div class="section-header">🔄 4. Análisis de Asimetría: In-Degree vs Out-Degree</div>', unsafe_allow_html=True)
    
    st.markdown(get_academic_context("in_out_degree"))
    
    selected_graph = st.selectbox(
        "Selecciona grafo para análisis detallado:",
        list(graphs.keys()),
        key="inout_selector"
    )
    
    fig_inout = plot_in_out_degree_comparison(
        graphs[selected_graph],
        title=f"In-Degree vs Out-Degree: {selected_graph}"
    )
    st.plotly_chart(fig_inout, use_container_width=True)
    
    # Hierarchical structure analysis
    st.subheader(f"Estructura Jerárquica: {selected_graph}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        hier_structure = analyze_hierarchical_structure(graphs[selected_graph])
        
        for key, value in hier_structure.items():
            st.metric(key, value)
    
    with col2:
        st.markdown(get_academic_context("hierarchical"))
    
    # ============================================
    # SECTION 5: Degree Correlation BGP ↔ RIPE
    # ============================================
    st.markdown('<div class="section-header">🔗 5. Correlación de Grado: Control-Plane ↔ Data-Plane</div>', unsafe_allow_html=True)
    
    st.markdown(get_academic_context("degree_correlation"))
    
    if "BGP" in graphs and "RIPE Atlas" in graphs:
        fig_corr = plot_degree_correlation(graphs["BGP"], graphs["RIPE Atlas"])
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.info("""
        **Análisis**: Los puntos cercanos a la línea y=x indican ASNs con conectividad consistente 
        entre control y data plane. Desviaciones significativas revelan ASNs con discrepancias 
        entre visibilidad BGP y tráfico real.
        """)
    
    # ============================================
    # SECTION 6: Top-K ASNs Comparison
    # ============================================
    st.markdown('<div class="section-header">🏆 6. Overlap Estructural: Top-K ASNs</div>', unsafe_allow_html=True)
    
    st.markdown(get_academic_context("top_k_overlap"))
    
    k_value = st.slider("Selecciona K (Top-K ASNs)", 10, 50, 20, step=5)
    
    fig_topk = plot_top_k_comparison(graphs, k=k_value)
    if fig_topk:
        st.plotly_chart(fig_topk, use_container_width=True)
    
    # Detailed Top-K tables
    st.subheader(f"Top-{k_value} ASNs por Grado")
    
    cols = st.columns(len(graphs))
    
    for idx, (name, g) in enumerate(graphs.items()):
        with cols[idx]:
            st.markdown(f"**{name}**")
            critical_asns = identify_critical_asns(g, metadatas[name], top_k=k_value)
            st.dataframe(critical_asns[["ASN", "Name", "Degree"]].head(10), 
                        hide_index=True)
    
    # ============================================
    # SECTION 7: Path Occurrences Analysis
    # ============================================
    st.markdown('<div class="section-header">🛤️ 7. Centralidad: Path Occurrences vs Degree</div>', unsafe_allow_html=True)
    
    st.markdown(get_academic_context("path_occurrences"))
    
    path_graph = st.selectbox(
        "Selecciona grafo:",
        [name for name, g in graphs.items() if "path_occurrences" in g.ndata],
        key="path_selector"
    )
    
    if path_graph:
        fig_path = plot_path_occurrences_vs_degree(
            graphs[path_graph],
            title=f"Path Occurrences vs Degree: {path_graph}"
        )
        if fig_path:
            st.plotly_chart(fig_path, use_container_width=True)
    
    # ============================================
    # SECTION 8: Critical ASNs Identification
    # ============================================
    st.markdown('<div class="section-header">🔥 8. Identificación de ASNs Críticos</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Los **ASNs críticos** combinan alta conectividad (degree) con alta centralidad (path occurrences).
    Estos nodos son fundamentales para la reachability y representan potenciales *single points of failure*.
    """)
    
    critical_graph = st.selectbox(
        "Selecciona grafo para análisis de criticidad:",
        list(graphs.keys()),
        key="critical_selector"
    )
    
    critical_df = identify_critical_asns(graphs[critical_graph], metadatas[critical_graph], top_k=30)
    st.dataframe(critical_df, use_container_width=True, hide_index=True)
    
    st.download_button(
        "📥 Descargar ASNs Críticos (CSV)",
        critical_df.to_csv(index=False).encode('utf-8'),
        f"critical_asns_{critical_graph.lower().replace(' ', '_')}.csv",
        "text/csv"
    )
    
    # ============================================
    # SECTION 9: Synthesis and Recommendations
    # ============================================
    # st.markdown('<div class="section-header">🎯 9. Síntesis y Recomendaciones</div>', unsafe_allow_html=True)
    
    # st.markdown(get_academic_context("comparison_summary"))
    
    # st.success("""
    # **Conclusiones Clave:**
    
    # 1. **Complementariedad de fuentes**: BGP y RIPE Atlas capturan aspectos diferentes pero complementarios 
    #    de la topología Internet. BGP provee amplitud (cobertura), RIPE provee profundidad (validación operacional).
    
    # 2. **Sesgo metodológico**: El bajo overlap es esperado y no problemático. Refleja diferencias en 
    #    visibilidad de routing vs tráfico real, especialmente para regiones con baja cobertura de probes RIPE.
    
    # 3. **Estructura jerárquica**: La asimetría in/out-degree confirma la naturaleza jerárquica de Internet,
    #    con clara distinción entre providers, transit, y stub ASNs.
    
    # 4. **Implicaciones para Chile**: La dependencia de pocos transit providers internacionales y la 
    #    concentración de conectividad en ASNs específicos sugiere vulnerabilidades estructurales.
    
    # 5. **Recomendación metodológica**: Para estudios de topología AS-level en Chile, utilizar el grafo **Merged**
    #    como base, complementado con análisis específicos de BGP (routing policies) y RIPE (conectividad operacional).
    # """)

elif analysis_mode == "📊 Individual por Grafo":
    # ============================================
    # INDIVIDUAL GRAPH ANALYSIS MODE
    # ============================================
    st.markdown('<div class="section-header">📊 Análisis Individual por Grafo</div>', unsafe_allow_html=True)
    
    selected_graph_name = st.selectbox(
        "Selecciona el grafo a analizar:",
        list(graphs.keys())
    )
    
    g = graphs[selected_graph_name]
    meta = metadatas[selected_graph_name]
    
    # Metrics
    st.subheader("📈 Métricas del Grafo")
    
    metrics = compute_advanced_metrics(g)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Nodos (ASNs)", metrics["Nodes"])
        st.metric("Aristas", metrics["Edges"])
    
    with col2:
        st.metric("Densidad", metrics["Density"])
        st.metric("Grado Promedio", metrics["Avg Degree"])
    
    with col3:
        st.metric("Grado Máximo", metrics["Max Degree"])
        st.metric("Grado Mediano", metrics["Median Degree"])
    
    with col4:
        st.metric("Ratio In/Out", metrics["In/Out Ratio"])
        st.metric("Gini (Concentración)", metrics["Degree Gini"])
    
    # Visualizations
    tabs = st.tabs(["Distribución de Grado", "In vs Out", "Path Occurrences", "ASNs Críticos"])
    
    with tabs[0]:
        fig = plot_degree_distribution_loglog(g, 
            title=f"Degree Distribution: {selected_graph_name}",
            color=COLORS.get(selected_graph_name, "#666"))
        st.plotly_chart(fig, use_container_width=True)
        
        dist_stats = analyze_degree_distribution(g)
        st.json(dist_stats)
    
    with tabs[1]:
        fig = plot_in_out_degree_comparison(g, 
            title=f"In-Degree vs Out-Degree: {selected_graph_name}")
        st.plotly_chart(fig, use_container_width=True)
        
        hier = analyze_hierarchical_structure(g)
        st.json(hier)
    
    with tabs[2]:
        if "path_occurrences" in g.ndata:
            fig = plot_path_occurrences_vs_degree(g, 
                title=f"Path Occurrences vs Degree: {selected_graph_name}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Path occurrences no disponible para este grafo")
    
    with tabs[3]:
        critical = identify_critical_asns(g, meta, top_k=50)
        st.dataframe(critical, use_container_width=True, hide_index=True)

else:
    # ============================================
    # CRITICAL ANALYSIS MODE
    # ============================================
    st.markdown('<div class="section-header">🎯 Análisis Individual de ASNs</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Permite analizar ASNs más críticos para la 
    topología de Internet en Chile.
    """)
    
    critical_graph = st.selectbox("Selecciona grafo:", list(graphs.keys()))
    
    g = graphs[critical_graph]
    meta = metadatas[critical_graph]
    
    # Compute critical ASNs
    top_k = st.slider("Top-K ASNs críticos", 10, 100, 30, step=10)
    
    critical_asns = identify_critical_asns(g, meta, top_k=top_k)
    
    st.subheader(f"Top-{top_k} ASNs Críticos en {critical_graph}")
    st.dataframe(critical_asns, use_container_width=True, hide_index=True)
    
    # Detailed analysis for selected ASN
    st.subheader("Análisis Detallado de ASN")
    
    selected_asn = st.selectbox(
        "Selecciona un ASN para análisis detallado:",
        critical_asns["ASN"].tolist(),
        format_func=lambda x: f"AS{x} - {critical_asns[critical_asns['ASN']==x]['Name'].iloc[0]}"
    )
    
    if selected_asn:
        asn_data = critical_asns[critical_asns["ASN"] == selected_asn].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("ASN", f"AS{asn_data['ASN']}")
            st.metric("Nombre", asn_data['Name'])
        
        with col2:
            st.metric("Degree Total", asn_data['Degree'])
            st.metric("In-Degree", asn_data['In-Degree'])
        
        with col3:
            st.metric("Out-Degree", asn_data['Out-Degree'])
            st.metric("Criticality Score", asn_data['Criticality Score'])
        
        st.info(f"""
        **Interpretación para AS{selected_asn}:**
        - **Degree**: {asn_data['Degree']} conexiones directas
        - **In-Degree**: {asn_data['In-Degree']} clientes (customers)
        - **Out-Degree**: {asn_data['Out-Degree']} proveedores (providers)
        - **Path Occurrences**: {asn_data['Path Occurrences']} apariciones en rutas
        
        Un alto criticality score indica que este ASN es fundamental para la conectividad
        de la red y su falla podría impactar significativamente la reachability.
        """)

# ==================================================
# Footer
# ==================================================
st.divider()

st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem 0;'>
    <p><strong>AS Topology Analyzer - Chile</strong></p>
    <p>Análisis Académico de Topologías AS-Level | NIC Chile Research Labs</p>
    <p><em>Datos: BGP RouteViews/RIS + RIPE Atlas Traceroute</em></p>
</div>
""", unsafe_allow_html=True)
