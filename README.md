# 🌐 AS Topology Visualizer - Chile

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Herramienta académica para análisis y visualización de topologías de Internet a nivel de Sistemas Autónomos (AS) en Chile. Compara datos de control-plane (BGP) y data-plane (RIPE Atlas/Traceroute) con análisis estadísticos avanzados y visualizaciones científicas.

---

## 📋 Contenido

- [Características](#-características)
- [Instalación Rápida](#-instalación-rápida)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Documentación](#-documentación)
- [Tecnologías](#-tecnologías)

---

## ✨ Características

### 🔬 Análisis Académico Riguroso
- **Métricas avanzadas**: Gini coefficient, Jaccard Index, Pearson correlation
- **Clasificación jerárquica**: Tier-1, Transit, Stub ASNs
- **Distribuciones power-law**: Análisis en escala log-log
- **Identificación de ASNs críticos**: Scoring compuesto basado en centralidad

### 📊 Visualizaciones Científicas
- **Diagramas de Venn**: Overlap profesional estilo paper académico
- **Gráficos log-log**: Para identificación de power-law
- **Scatter plots con correlación**: Pearson r para control vs data plane
- **Comparaciones multi-fuente**: BGP, RIPE Atlas, Merged

### 🎯 Tres Modos de Análisis
1. **Modo Comparativo**: Análisis lado a lado de las 3 fuentes (9 secciones)
2. **Modo Individual**: Deep dive por grafo
3. **Modo Crítico**: Análisis ASN-específico

---

## 🚀 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/valesteban/as-topology-visualizer-cl.git
cd as-topology-visualizer-cl

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python test_environment.py
```

---

## 💻 Uso

### Iniciar Aplicación Académica
```bash
streamlit run app/app_academic.py
```

La aplicación se abrirá en `http://localhost:8501`

---

## 📁 Estructura del Proyecto

```
as-topology-visualizer-cl/
├── app/
│   ├── app.py                    # Aplicación simple
│   └── app_academic.py           # Aplicación académica completa ⭐
├── data/csv/                     # Datos BGP, RIPE Atlas, Merged
├── src/
│   ├── analysis.py               # Métricas avanzadas ⭐
│   ├── visualizations.py         # Gráficos científicos ⭐
│   └── interpretations.py        # Contexto académico ⭐
├── docs/                         # Documentación completa
└── requirements.txt
```

---

## 📚 Documentación

### Para Tesis y Papers

1. **[README_ACADEMIC.md](README_ACADEMIC.md)** - Guía académica completa
2. **[GUIA_INTERPRETACION.md](GUIA_INTERPRETACION.md)** - Interpretación de resultados
3. **[RECOMENDACIONES_ACADEMICAS.md](RECOMENDACIONES_ACADEMICAS.md)** - Tips para escritura
4. **[PASO_A_PASO.md](PASO_A_PASO.md)** ⭐ - Explicación detallada del proyecto

---

## 🔧 Tecnologías

- **Python 3.10+**: Lenguaje base
- **Streamlit**: Framework web interactivo
- **DGL 1.1.3**: Análisis de grafos
- **PyTorch 2.4.1**: Backend tensorial
- **Plotly 6.5**: Visualizaciones interactivas
- **Matplotlib**: Gráficos estáticos profesionales
- **SciPy**: Estadística avanzada

---

## 🎓 Para tu Tesis

✅ Figuras listas para publicar (300+ DPI)  
✅ Métricas validadas académicamente  
✅ Interpretaciones con referencias bibliográficas  
✅ Ejemplos de redacción para papers  

---

## 📞 Contacto

- GitHub: [@valesteban](https://github.com/valesteban)
- Repositorio: [as-topology-visualizer-cl](https://github.com/valesteban/as-topology-visualizer-cl)

---

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para más detalles.
- Visualización vía Streamlit

## Run
```bash
streamlit run app/app.py
