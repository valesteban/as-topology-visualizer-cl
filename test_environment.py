#!/usr/bin/env python3
"""
Script de prueba para verificar que el entorno está correctamente configurado
y que todas las dependencias funcionan correctamente.
"""

import sys
from pathlib import Path

def test_imports():
    """Prueba la importación de todas las dependencias principales"""
    print("🔍 Probando importación de dependencias...\n")
    
    errors = []
    
    # Test Streamlit
    try:
        import streamlit as st
        print(f"✅ Streamlit {st.__version__}")
    except Exception as e:
        errors.append(f"❌ Streamlit: {e}")
        print(f"❌ Streamlit: {e}")
    
    # Test Pandas
    try:
        import pandas as pd
        print(f"✅ Pandas {pd.__version__}")
    except Exception as e:
        errors.append(f"❌ Pandas: {e}")
        print(f"❌ Pandas: {e}")
    
    # Test NumPy
    try:
        import numpy as np
        print(f"✅ NumPy {np.__version__}")
    except Exception as e:
        errors.append(f"❌ NumPy: {e}")
        print(f"❌ NumPy: {e}")
    
    # Test PyTorch
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"   GPU disponible: {torch.cuda.get_device_name(0)}")
        else:
            print("   GPU no disponible (usando CPU)")
    except Exception as e:
        errors.append(f"❌ PyTorch: {e}")
        print(f"❌ PyTorch: {e}")
    
    # Test DGL
    try:
        import dgl
        print(f"✅ DGL {dgl.__version__}")
    except Exception as e:
        errors.append(f"❌ DGL: {e}")
        print(f"❌ DGL: {e}")
    
    # Test PyYAML
    try:
        import yaml
        print(f"✅ PyYAML {yaml.__version__}")
    except Exception as e:
        errors.append(f"❌ PyYAML: {e}")
        print(f"❌ PyYAML: {e}")
    
    return errors


def test_data_files():
    """Verifica que los archivos de datos existan"""
    print("\n\n📁 Verificando archivos de datos...\n")
    
    errors = []
    
    data_files = [
        "data/csv/bgp/nodes.csv",
        "data/csv/bgp/edges.csv",
        "data/csv/ripe_atlas/nodes.csv",
        "data/csv/ripe_atlas/edges.csv",
    ]
    
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            errors.append(f"❌ No encontrado: {file_path}")
            print(f"❌ No encontrado: {file_path}")
    
    return errors


def test_graph_loading():
    """Prueba la carga de un grafo simple"""
    print("\n\n📊 Probando carga de grafo...\n")
    
    try:
        sys.path.append(str(Path(__file__).resolve().parents[0]))
        from src.io.load_csv_graph import load_graph_from_csv
        
        # Intenta cargar el grafo BGP
        g, metadata = load_graph_from_csv(
            nodes_csv_path=Path("data/csv/bgp/nodes.csv"),
            edges_csv_path=Path("data/csv/bgp/edges.csv")
        )
        
        print(f"✅ Grafo cargado exitosamente")
        print(f"   Nodos: {g.num_nodes()}")
        print(f"   Aristas: {g.num_edges()}")
        
        return []
    except FileNotFoundError as e:
        error = f"❌ Archivo no encontrado: {e}"
        print(error)
        return [error]
    except Exception as e:
        error = f"❌ Error al cargar grafo: {e}"
        print(error)
        return [error]


def main():
    print("=" * 60)
    print("🧪 PRUEBA DE ENTORNO VIRTUAL")
    print("AS Topology Visualizer - Chile")
    print("=" * 60)
    print()
    
    # Ejecutar pruebas
    import_errors = test_imports()
    data_errors = test_data_files()
    graph_errors = test_graph_loading()
    
    # Resumen
    print("\n\n" + "=" * 60)
    print("📋 RESUMEN")
    print("=" * 60)
    
    all_errors = import_errors + data_errors + graph_errors
    
    if not all_errors:
        print("\n✅ ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("\n🚀 El entorno está listo para usar.")
        print("   Para ejecutar la aplicación, usa:")
        print("   streamlit run app/app.py")
        return 0
    else:
        print(f"\n❌ Se encontraron {len(all_errors)} error(es):")
        for error in all_errors:
            print(f"   {error}")
        print("\n⚠️  Por favor, revisa los errores antes de continuar.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
