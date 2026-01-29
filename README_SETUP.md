# Configuración del Entorno Virtual

Este documento describe cómo configurar y usar el entorno virtual para el proyecto AS Topology Visualizer.

## Requisitos previos

- Python 3.10.13 (recomendado) o superior
- pip instalado

## Configuración inicial

### 1. Activar el entorno virtual

El entorno virtual ya está creado en la carpeta `venv/`. Para activarlo:

```bash
source venv/bin/activate
```

## Verificar la instalación

### Opción 1: Usar el script de prueba (recomendado)

```bash
python test_environment.py
```

Este script verificará:
- ✅ Todas las dependencias se importan correctamente
- ✅ Los archivos de datos existen
- ✅ Los grafos se pueden cargar correctamente

### Opción 2: Ver paquetes instalados

```bash
pip list
```

## Ejecutar la aplicación

Una vez activado el entorno virtual, puedes ejecutar la aplicación de Streamlit:

```bash
streamlit run app/app.py
```

## Dependencias instaladas

El proyecto incluye las siguientes dependencias principales:

- **streamlit**: Framework para la aplicación web
- **pandas**: Manejo de datos tabulares
- **numpy**: Operaciones numéricas
- **torch**: PyTorch para grafos y tensores
- **dgl**: Deep Graph Library para grafos
- **pyyaml**: Lectura de archivos de configuración YAML

## Desactivar el entorno virtual

Para salir del entorno virtual:

```bash
deactivate
```

## Reinstalar dependencias

Si necesitas reinstalar las dependencias desde cero:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Notas

- El entorno virtual está configurado para ignorarse en git (ver `.gitignore`)
- Si encuentras problemas con CUDA/GPU, las librerías de NVIDIA se instalarán automáticamente con PyTorch
- Para desarrollo, asegúrate de siempre tener el entorno virtual activado
