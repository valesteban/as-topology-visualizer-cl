"""
Módulo de análisis académico para topologías AS-level.
Incluye métricas avanzadas, análisis de centralidad y comparaciones estructurales.
"""

import numpy as np
import pandas as pd
import torch
from collections import Counter


def compute_advanced_metrics(g):
    """
    Calcula métricas avanzadas de topología de grafos.
    """
    in_deg = g.in_degrees().numpy()
    out_deg = g.out_degrees().numpy()
    deg = in_deg + out_deg
    
    num_nodes = g.num_nodes()
    num_edges = g.num_edges()
    
    # Densidad del grafo
    max_edges = num_nodes * (num_nodes - 1)  # Dirigido
    density = num_edges / max_edges if max_edges > 0 else 0
    
    # Grado promedio
    avg_degree = float(deg.mean()) if num_nodes > 0 else 0
    
    # Asimetría in/out degree (indicador de jerarquía)
    in_out_ratio = float(in_deg.mean() / out_deg.mean()) if out_deg.mean() > 0 else np.inf
    
    # Nodos stub (degree = 1), intermedios, y hubs (degree > percentil 90)
    stub_nodes = int(np.sum(deg == 1))
    percentile_90 = np.percentile(deg[deg > 0], 90) if len(deg[deg > 0]) > 0 else 0
    hub_nodes = int(np.sum(deg >= percentile_90))
    
    # Concentración de grado (Gini coefficient aproximado)
    if len(deg) > 0:
        sorted_deg = np.sort(deg)
        n = len(sorted_deg)
        cumsum = np.cumsum(sorted_deg)
        gini = (2 * np.sum((np.arange(n) + 1) * sorted_deg)) / (n * cumsum[-1]) - (n + 1) / n if cumsum[-1] > 0 else 0
    else:
        gini = 0
    
    metrics = {
        "Nodes": num_nodes,
        "Edges": num_edges,
        "Density": f"{density:.6f}",
        "Avg Degree": f"{avg_degree:.2f}",
        "Max Degree": int(deg.max()) if num_nodes > 0 else 0,
        "Median Degree": int(np.median(deg)) if num_nodes > 0 else 0,
        "Std Degree": f"{deg.std():.2f}" if num_nodes > 0 else "0.00",
        "In/Out Ratio": f"{in_out_ratio:.2f}",
        "Stub Nodes (deg=1)": stub_nodes,
        "Hub Nodes (top 10%)": hub_nodes,
        "Degree Gini": f"{gini:.3f}",
    }
    
    return metrics


def compare_graph_metrics(graphs_dict):
    """
    Compara métricas entre múltiples grafos.
    Retorna un DataFrame con métricas lado a lado.
    """
    all_metrics = {}
    
    for name, g in graphs_dict.items():
        all_metrics[name] = compute_advanced_metrics(g)
    
    df = pd.DataFrame(all_metrics).T
    return df


def compute_asn_overlap_metrics(g_bgp, g_ripe):
    """
    Calcula métricas de overlap entre BGP y RIPE Atlas.
    """
    asns_bgp = set(g_bgp.ndata["asn"].numpy())
    asns_ripe = set(g_ripe.ndata["asn"].numpy())
    
    overlap = asns_bgp & asns_ripe
    only_bgp = asns_bgp - asns_ripe
    only_ripe = asns_ripe - asns_bgp
    total = asns_bgp | asns_ripe
    
    jaccard = len(overlap) / len(total) if len(total) > 0 else 0
    bgp_coverage = len(overlap) / len(asns_bgp) if len(asns_bgp) > 0 else 0
    ripe_coverage = len(overlap) / len(asns_ripe) if len(asns_ripe) > 0 else 0
    
    metrics = {
        "Total Unique ASNs": len(total),
        "ASNs in BGP": len(asns_bgp),
        "ASNs in RIPE": len(asns_ripe),
        "Overlap ASNs": len(overlap),
        "Only BGP": len(only_bgp),
        "Only RIPE": len(only_ripe),
        "Jaccard Index": f"{jaccard:.3f}",
        "BGP Coverage": f"{bgp_coverage:.2%}",
        "RIPE Coverage": f"{ripe_coverage:.2%}",
    }
    
    return metrics


def analyze_degree_distribution(g):
    """
    Analiza la distribución de grado y retorna estadísticas descriptivas.
    """
    degrees = (g.in_degrees() + g.out_degrees()).numpy()
    degrees = degrees[degrees > 0]  # Filtrar degree 0
    
    if len(degrees) == 0:
        return {
            "Mean": 0,
            "Median": 0,
            "Mode": 0,
            "Std": 0,
            "Skewness": 0,
            "P25": 0,
            "P75": 0,
            "P90": 0,
            "P95": 0,
            "P99": 0,
        }
    
    from scipy import stats
    
    analysis = {
        "Mean": f"{degrees.mean():.2f}",
        "Median": int(np.median(degrees)),
        "Mode": int(stats.mode(degrees, keepdims=True)[0][0]),
        "Std": f"{degrees.std():.2f}",
        "Skewness": f"{stats.skew(degrees):.2f}",
        "P25": int(np.percentile(degrees, 25)),
        "P75": int(np.percentile(degrees, 75)),
        "P90": int(np.percentile(degrees, 90)),
        "P95": int(np.percentile(degrees, 95)),
        "P99": int(np.percentile(degrees, 99)),
    }
    
    return analysis


def identify_critical_asns(g, node_metadata, top_k=20):
    """
    Identifica ASNs críticos basados en múltiples métricas.
    Combina: degree, path_occurrences, betweenness (proxy).
    """
    degrees = (g.in_degrees() + g.out_degrees()).numpy()
    asns = g.ndata["asn"].numpy()
    
    if "path_occurrences" in g.ndata:
        paths = g.ndata["path_occurrences"].numpy()
    else:
        paths = np.zeros_like(degrees)
    
    # Score compuesto (normalizado)
    degree_norm = degrees / (degrees.max() + 1e-10)
    paths_norm = paths / (paths.max() + 1e-10)
    
    # Score = weighted average
    scores = 0.5 * degree_norm + 0.5 * paths_norm
    
    # Top K
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            "ASN": int(asns[idx]),
            "Name": node_metadata.get("name", {}).get(idx, "Unknown"),
            "Degree": int(degrees[idx]),
            "In-Degree": int(g.in_degrees()[idx]),
            "Out-Degree": int(g.out_degrees()[idx]),
            "Path Occurrences": int(paths[idx]),
            "Criticality Score": f"{scores[idx]:.4f}"
        })
    
    return pd.DataFrame(results)


def analyze_hierarchical_structure(g):
    """
    Analiza la estructura jerárquica del grafo basado en ratios in/out degree.
    Clasifica nodos en: Tier-1 (providers), Transit, Stub.
    """
    in_deg = g.in_degrees().numpy()
    out_deg = g.out_degrees().numpy()
    total_deg = in_deg + out_deg
    
    # Clasificación heurística
    # Tier-1: alto out-degree, bajo in-degree (muchos clientes, pocos providers)
    # Transit: balance entre in y out
    # Stub: bajo out-degree o degree = 1
    
    tier1_candidates = (out_deg > 10) & (in_deg < 5)
    transit_candidates = (total_deg > 5) & ~tier1_candidates
    stub_candidates = (total_deg <= 5) | (total_deg == 1)
    
    classification = {
        "Tier-1 Candidates": int(tier1_candidates.sum()),
        "Transit ASNs": int(transit_candidates.sum()),
        "Stub ASNs": int(stub_candidates.sum()),
        "Tier-1 %": f"{100 * tier1_candidates.sum() / len(tier1_candidates):.1f}%",
        "Transit %": f"{100 * transit_candidates.sum() / len(transit_candidates):.1f}%",
        "Stub %": f"{100 * stub_candidates.sum() / len(stub_candidates):.1f}%",
    }
    
    return classification


def compute_edge_overlap(g_bgp, g_ripe):
    """
    Calcula el overlap de aristas entre BGP y RIPE Atlas.
    """
    # Extraer aristas como tuplas (src, dst)
    edges_bgp = set()
    src_bgp, dst_bgp = g_bgp.edges()
    asns_bgp = g_bgp.ndata["asn"].numpy()
    
    for i in range(len(src_bgp)):
        s = int(asns_bgp[src_bgp[i]])
        d = int(asns_bgp[dst_bgp[i]])
        edges_bgp.add((s, d))
    
    edges_ripe = set()
    src_ripe, dst_ripe = g_ripe.edges()
    asns_ripe = g_ripe.ndata["asn"].numpy()
    
    for i in range(len(src_ripe)):
        s = int(asns_ripe[src_ripe[i]])
        d = int(asns_ripe[dst_ripe[i]])
        edges_ripe.add((s, d))
    
    overlap = edges_bgp & edges_ripe
    only_bgp = edges_bgp - edges_ripe
    only_ripe = edges_ripe - edges_bgp
    total = edges_bgp | edges_ripe
    
    jaccard = len(overlap) / len(total) if len(total) > 0 else 0
    
    metrics = {
        "Total Unique Edges": len(total),
        "Edges in BGP": len(edges_bgp),
        "Edges in RIPE": len(edges_ripe),
        "Overlap Edges": len(overlap),
        "Only BGP": len(only_bgp),
        "Only RIPE": len(only_ripe),
        "Jaccard Index": f"{jaccard:.3f}",
        "BGP Edge Coverage": f"{len(overlap) / len(edges_bgp):.2%}" if len(edges_bgp) > 0 else "N/A",
        "RIPE Edge Coverage": f"{len(overlap) / len(edges_ripe):.2%}" if len(edges_ripe) > 0 else "N/A",
    }
    
    return metrics


def generate_academic_summary(graphs_dict, node_metadatas):
    """
    Genera un resumen académico completo de los grafos.
    """
    summary = {
        "Graph Metrics": {},
        "Overlap Analysis": {},
        "Degree Distribution": {},
        "Hierarchical Structure": {},
    }
    
    # Métricas básicas
    for name, g in graphs_dict.items():
        summary["Graph Metrics"][name] = compute_advanced_metrics(g)
        summary["Degree Distribution"][name] = analyze_degree_distribution(g)
        summary["Hierarchical Structure"][name] = analyze_hierarchical_structure(g)
    
    # Análisis de overlap
    if "BGP" in graphs_dict and "RIPE Atlas" in graphs_dict:
        summary["Overlap Analysis"]["ASN Overlap"] = compute_asn_overlap_metrics(
            graphs_dict["BGP"],
            graphs_dict["RIPE Atlas"]
        )
        summary["Overlap Analysis"]["Edge Overlap"] = compute_edge_overlap(
            graphs_dict["BGP"],
            graphs_dict["RIPE Atlas"]
        )
    
    return summary
