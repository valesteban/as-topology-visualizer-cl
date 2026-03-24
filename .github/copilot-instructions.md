# Instrucciones de Copilot para as-topology-visualizer-cl

## Panorama del proyecto
- La app de Streamlit en `app/app_academic.py` orquesta la UI de análisis y carga grafos con `src/load_csv_graph.py`.
- Pipeline principal: CSVs en `data/csv/{bgp,ripe_atlas,merged}/` → `load_graph_from_csv()` construye grafos DGL → `src/analysis.py` calcula métricas → `src/visualizations.py` renderiza figuras → `src/interpretations.py` aporta textos académicos.
- Las fuentes representan control-plane (BGP), data-plane (RIPE Atlas) y vista combinada; la mayoría de comparaciones asumen claves `"BGP"`, `"RIPE Atlas"`, `"Merged"` en el diccionario de grafos.

## Convenciones de datos y grafos
- Entradas CSV: `nodes.csv` (debe incluir `asn`; puede incluir `in_degree`, `out_degree`, `path_occurrences`, `name` opcional) y `edges.csv` (`src_id`, `dst_id`, `weight` opcional).
- `load_graph_from_csv()` adjunta tensores numéricos de nodo (p. ej., `g.ndata["asn"]`) y retorna `node_metadata["name"]` para mostrar en tablas y PyVis.

## Módulos y patrones clave
- `src/analysis.py` es el hub de métricas (p. ej., `compute_advanced_metrics`, `compute_edge_overlap`, `analyze_hierarchical_structure`).
- `identify_critical_asns(g, node_metadata, top_k=20)` espera que `node_metadata` mapee ids de nodo a nombres.
- `src/visualizations.py` centraliza gráficos y usa la paleta compartida `COLORS` (BGP/RIPE/Merged); mantén nuevos plots alineados a esta paleta.
- `build_pyvis_network()` submuestrea grafos grandes con `_select_top_nodes_by_degree()` para mantener la UI responsiva.
- Cache de Streamlit: `@st.cache_data` envuelve `load_all_graphs()` en `app/app_academic.py` para recargas más rápidas.

## Flujos de trabajo de desarrollo
- Ejecutar la app académica: `streamlit run app/app_academic.py` (requiere deps en `requirements.txt` y CSVs en `data/csv/`).
- Diagnóstico: `test_edge_overlap.py` es un script standalone para validar `compute_edge_overlap()` con CSVs.

## Notebooks y documentación
- Los notebooks viven en `noteebooks/` (usados para slides y trabajo exploratorio).
- Notas arquitectónicas profundas en `PASO_A_PASO.md` y guía académica en `README_ACADEMIC.md`.
