#!/bin/bash
# Script para activar el entorno virtual y ejecutar la aplicación

echo "🔧 Activando entorno virtual..."
source venv/bin/activate

echo "✅ Entorno virtual activado"
echo ""
echo "Para ejecutar la aplicación, usa:"
echo "  streamlit run app/app.py"
echo ""
echo "Para desactivar el entorno, usa:"
echo "  deactivate"
echo ""
