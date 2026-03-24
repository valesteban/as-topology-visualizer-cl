# Script para activar el entorno virtual y mostrar comandos utiles (PowerShell)

$activateScript = ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    $activateScript = "venv\Scripts\Activate.ps1"
}

if (-not (Test-Path $activateScript)) {
    Write-Error "No se encontro el script de activacion. Esperado en '.venv\\Scripts\\Activate.ps1' o 'venv\\Scripts\\Activate.ps1'."
    exit 1
}

Write-Host "Activando entorno virtual..."
. $activateScript

Write-Host "Entorno virtual activado"
Write-Host ""
Write-Host "Para ejecutar la aplicacion, usa:"
Write-Host "  streamlit run app/app_academic.py"
Write-Host ""
Write-Host "Para desactivar el entorno, usa:"
Write-Host "  deactivate"
Write-Host ""
