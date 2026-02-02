"""
Módulo de interpretaciones académicas para visualizaciones de topologías AS-level.
Provee contexto, explicaciones y análisis textuales para cada tipo de visualización.
"""


def interpret_degree_distribution():
    """Interpretación de la distribución de grado."""
    return """
    ### 📊 Interpretación: Distribución de Grado
    
    La **distribución de grado** en topologías AS-level nos muestrras un comportamiento 
    **power-law** (ley de potencias).
    
    **Características observables:**
    - **Mayoría de ASNs con grado bajo**: Corresponden a *stub ASNs* (redes de borde) que solo se conectan 
      a uno o pocos proveedores upstream.
    - **Pocos ASNs con grado muy alto**: Representan *transit providers* y Tier-1 ISPs que actúan como 
      backbone de Internet, conectando múltiples redes.
    
    """

    # **Implicaciones:**
    # - **Robustez y vulnerabilidad**: Las redes scale-free son robustas ante fallas aleatorias pero 
    #   vulnerables a ataques dirigidos contra hubs.
    # - **Centralización**: La existencia de hubs indica una topología jerárquica con concentración de 
    #   conectividad en pocos actores.

def interpret_in_out_degree():
    """Interpretación de la asimetría in-degree vs out-degree."""
    return """
    ### 📊 Interpretación: In-Degree vs Out-Degree
    
    La **asimetría entre in-degree y out-degree** revela la **estructura jerárquica** de relaciones 
    provider-customer en Internet:
    
    **In-degree** (aristas entrantes):
    - Representa el número de **clientes** (customers) que un AS tiene.
    - ASNs con alto in-degree son típicamente *transit providers* o Tier-1 ISPs.
    - Un in-degree alto indica un rol de *provider*.
    
    **Out-degree** (aristas salientes):
    - Representa el número de **proveedores** (providers) a los que un AS se conecta.
    - Un out-degree bajo indica dependencia de pocos upstreams.
    

    **Contexto Chile:**
    - Predominancia de stub ASNs con out-degree 1-2 sugiere dependencia de pocos proveedores internacionales.
    - Pocos ASNs con alto in-degree indican mercado concentrado en transit providers locales.
    """
    # **Patrones esperados:**
    # - **Tier-1 ASNs**: Alto in-degree, bajo out-degree (muchos clientes, relaciones peer-to-peer).
    # - **Stub ASNs**: Bajo in-degree (0-1), bajo out-degree (1-3 providers).
    # - **Transit ASNs**: Balance moderado entre in y out-degree.
    

def interpret_bgp_vs_ripe():
    """Interpretación de diferencias entre BGP y RIPE Atlas."""
    return """
    ### 📊 Interpretación: Control-Plane (BGP) vs Data-Plane (RIPE Atlas)
    
    Las **diferencias fundamentales** entre BGP y RIPE Atlas reflejan dos perspectivas complementarias 
    de la topología de Internet:
    
    **BGP (Control-Plane):**
    - **Visión completa de routing**: Captura todas las relaciones AS-to-AS anunciadas en BGP, 
      incluyendo paths que pueden no ser activamente utilizados.
    - **Sesgo hacia Tier-1/Transit**: Sobre-representa ASNs grandes con amplia visibilidad en routing tables.
    - **Incluye paths no utilizados**: Rutas anunciadas pero no necesariamente transitadas por tráfico real.
    - **Cobertura global**: Routing Information Bases (RIBs) capturan una vista amplia del routing.
    
    **RIPE Atlas (Data-Plane):**
    - **Rutas activas reales**: Solo captura paths efectivamente utilizados por tráfico de mediciones (traceroute).
    - **Sesgo geográfico**: Limitado por ubicación de probes RIPE Atlas (concentración en Europa, menor en América Latina).
    - **Sesgo temporal**: Depende de cuándo y desde dónde se ejecutan mediciones.
    - **Rutas operacionales**: Refleja el plano de datos, lo que realmente se usa para transportar tráfico.
    
    **Consecuencias del bajo overlap:**
    - **ASNs visibles solo en BGP**: Redes anunciadas pero sin tráfico observable desde RIPE Atlas 
      (pueden ser stub ASNs sin probes, o ASNs en regiones poco monitoreadas).
    - **ASNs visibles solo en RIPE**: Poco probable, pero puede ocurrir con ASNs que no exportan rutas 
      ampliamente pero sí son transitados (e.g., IXPs privados).
    - **Complementariedad**: BGP aporta cobertura, RIPE aporta validación de uso real.
    
    **Para Chile:**
    - Baja presencia de probes RIPE en Latinoamérica → subrepresentación en data-plane.
    - ASNs chilenos principalmente visibles en BGP, menos en traceroutes desde Europa.
    """


def interpret_degree_correlation():
    """Interpretación de la correlación de grado BGP vs RIPE."""
    return """
    ###"""



def interpret_top_k_overlap():
    """Interpretación del overlap de top-K ASNs."""
    return """
    """


def interpret_path_occurrences():
    """Interpretación de path occurrences vs degree."""
    return """
    ### 📊 Interpretación: Path Occurrences vs Degree
    
    La relación entre **path occurrences** (centralidad en rutas) y **degree** (conectividad) 
    distingue entre *conectividad estructural* y *centralidad de tránsito*:
    
    **Path occurrences:**
    - Mide cuántas veces un ASN aparece en rutas BGP o traceroutes.
    - Alto valor indica que el AS es frecuentemente transitado.
    
    **Degree:**
    - Mide cuántos vecinos directos tiene un AS.
    - Alto valor indica muchas conexiones, pero no necesariamente tránsito.
    
    """


    # **Patrones esperados:**
    
    # 1. **Correlación positiva fuerte:**
    #    - ASNs con alto degree también tienen alto path occurrences.
    #    - Típico de Tier-1 y backbone ISPs: muchas conexiones y mucho tránsito.
    
    # 2. **Alto degree, bajo path occurrences:**
    #    - ASNs con muchas conexiones pero poco tránsito.
    #    - Puede ser: route collectors, IXPs, o ASNs con peers que no generan tráfico.
    
    # 3. **Bajo degree, alto path occurrences:**
    #    - ASNs en posiciones críticas con pocas conexiones pero alta centralidad.
    #    - Bottlenecks: ASNs que son únicos caminos para alcanzar ciertas redes.
    
    # 4. **Bajo degree, bajo path occurrences:**
    #    - Stub ASNs: redes de borde sin tránsito.
    
    # **Implicaciones:**
    # - ASNs con alto path occurrences son **críticos para reachability**.
    # - Identificar ASNs con path occurrences desproporcionado vs degree señala *single points of failure*.
def interpret_asn_overlap_venn():
    """Interpretación del diagrama de overlap de ASNs."""
    return """
    ### 📊 Interpretación: Overlap de ASNs (BGP ∩ RIPE)
    
    El **bajo overlap** entre ASNs observados en BGP y RIPE Atlas:
    
    **ASNs solo en BGP (mayoría):**
    - **Stub ASNs sin tráfico RIPE o regiones sin cobertura RIPE**: Redes pequeñas o regionales sin probes RIPE cercanos.
    - **Rutas anunciadas pero no utilizadas**: Prefijos BGP que no son activamente alcanzados por traceroutes.
    - **BGP routing tables contienen millones de prefijos**.
    
    
    **ASNs en overlap (núcleo):**
    - **Core Internet ASNs**: Tier-1 ISPs, grandes transit providers, CDNs globales.
    - **ASNs con amplia visibilidad**: Presentes en routing tables y activamente transitados.
    - **ASNs en zonas con probes RIPE**.

    **Grafo AS-level en Chile:**
    - Grafo BGP: mejor cobertura de ASNs chilenos.
    - Grafo RIPE: valida cuáles ASNs son realmente transitados en rutas.
    - Grafo Merged: combina lo mejor de ambos mundos.
    
    """

    # **Jaccard Index bajo (~0.1-0.3):**
    # - Normal para comparaciones BGP vs traceroute.
    # - No indica problema, sino complementariedad de fuentes:
    #   - **BGP**: Amplitud, cobertura global, routing policies.
    #   - **RIPE**: Profundidad, validación operacional, rutas reales.
    
    # **Para estudios AS-level en Chile:**
    # - Grafo BGP: mejor cobertura de ASNs chilenos.
    # - Grafo RIPE: valida cuáles ASNs son realmente transitados en rutas internacionales.
    # # - Grafo Merged: combina lo mejor de ambos mundos.

def interpret_hierarchical_structure():
    """Interpretación de la estructura jerárquica."""
    return """
    ### 📊 Interpretación: Estructura Jerárquica de Internet
    
    La topología AS-level exhibe una **jerarquía clara** reflejada en la clasificación de ASNs:
    
    **Tier-1 ASNs (alto out-degree, bajo in-degree):**
    - **Proveedores globales** sin upstream propio (settlement-free peering).
    - Ejemplos: Cogent (174), Hurricane Electric (6939), NTT (2914), Telia (1299).
    - Representan el **backbone de Internet**: rutas entre ellos son gratuitas (peering), 
      pero venden tránsito a clientes downstream.
    
    **Transit ASNs (balance in/out):**
    - **ISPs regionales o nacionales** que compran tránsito de Tier-1 y venden a clientes locales.
    - Actúan como intermediarios: tienen providers (out-degree) y clientes (in-degree).
    - En Chile: operadores como Telefónica/Movistar, Entel, GTD.
    
    **Stub ASNs (bajo degree, mayormente out):**
    - **Redes de borde**: universidades, empresas, ISPs pequeños.
    - Solo compran tránsito, no venden (no tienen clientes BGP).
    
    
    **Chile:**
    - Alta proporción de stub ASNs refleja mercado con pocos proveedores dominantes.
    - Dependencia de conectividad internacional vía pocos transit ASNs.
    """

    # **Stub ASNs (bajo degree, mayormente out):**
    # - **Redes de borde**: universidades, empresas, ISPs pequeños.
    # - Solo compran tránsito, no venden (no tienen clientes BGP).
    # - Representan la mayoría de ASNs (~80-90% en topologías globales).
    # **Implicaciones:**
    # - **Centralización**: Concentración de poder en pocos Tier-1.
    # - **Dependencia**: Stub ASNs dependen críticamente de sus proveedores.
    # - **Políticas de routing**: Las relaciones customer-provider determinan preferencias de rutas (Gao-Rexford).
    

def interpret_comparison_summary():
    """Resumen interpretativo de la comparación entre grafos."""
    return """
    ### 🎯 Síntesis: BGP vs RIPE Atlas vs Merged
    
    **BGP (Control-Plane):**
    - ✅ **Fortalezas**: Cobertura global, captura routing policies, amplitud de ASNs.
    - ❌ **Limitaciones**: Incluye rutas no utilizadas, sesgo hacia grandes ISPs, no valida tráfico real.
    - 📊 **Mejor para**: Análisis de estructura jerárquica, políticas de routing, cobertura exhaustiva.
    
    **RIPE Atlas (Data-Plane):**
    - ✅ **Fortalezas**: Validación operacional, rutas reales, visibilidad de uso efectivo.
    - ❌ **Limitaciones**: Sesgo geográfico (Europa), cobertura parcial, dependiente de probes.
    - 📊 **Mejor para**: Validar conectividad real, medir latencias, identificar rutas activas.
    
    **Merged (Hybrid):**
    - ✅ **Fortalezas**: Combina amplitud de BGP con validación de RIPE, visión más completa.
    - ❌ **Limitaciones**: Mayor complejidad, posible redundancia, pesos de aristas ambiguos.
    - 📊 **Mejor para**: Análisis comprehensivo, estudios que requieren máxima cobertura y realismo.
    
    **Recomendación:**
    - **Para topología AS-level de Chile**: Usar **Merged** como referencia principal, 
      con análisis separados de BGP y RIPE para entender sesgos específicos.
    - **Para estudios de reachability**: Priorizar **RIPE Atlas** (data-plane real).
    - **Para estudios de routing policies**: Priorizar **BGP** (control-plane completo).
    """


def get_academic_context(section):
    """
    Retorna el contexto académico apropiado para cada sección.
    """
    contexts = {
        "degree_distribution": interpret_degree_distribution(),
        "in_out_degree": interpret_in_out_degree(),
        "bgp_vs_ripe": interpret_bgp_vs_ripe(),
        "degree_correlation": interpret_degree_correlation(),
        "top_k_overlap": interpret_top_k_overlap(),
        "path_occurrences": interpret_path_occurrences(),
        "asn_overlap": interpret_asn_overlap_venn(),
        "hierarchical": interpret_hierarchical_structure(),
        "comparison_summary": interpret_comparison_summary(),
    }
    
    return contexts.get(section, "")
