@echo off
REM Script para activar el entorno virtual y mostrar comandos utiles (CMD)

set "ACTIVATE_SCRIPT=.venv\Scripts\activate.bat"
if not exist "%ACTIVATE_SCRIPT%" set "ACTIVATE_SCRIPT=venv\Scripts\activate.bat"

if not exist "%ACTIVATE_SCRIPT%" (
    echo No se encontro el script de activacion.
    echo Esperado en ".venv\Scripts\activate.bat" o "venv\Scripts\activate.bat".
    exit /b 1
)

echo Activando entorno virtual...
call "%ACTIVATE_SCRIPT%"

echo Entorno virtual activado
echo.
echo Para ejecutar la aplicacion, usa:
echo   streamlit run app/app_academic.py
echo.
echo Para desactivar el entorno, usa:
echo   deactivate
echo.
