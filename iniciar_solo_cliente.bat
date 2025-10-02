@echo off
setlocal

REM === CONFIGURACIÓN ===
set "CONDA_ENV=base"
set "PROYECTO_DIR=C:\Users\Hans\Documents\Github\Universidad\Proyecto1_SD"
set "CONDA_ACTIVATE=C:\Users\Hans\miniconda3\Scripts\activate.bat"

REM Cambiar al directorio del proyecto
cd /d "%PROYECTO_DIR%"

REM Iniciar cliente
start "Cliente" cmd /k "call "%CONDA_ACTIVATE%" %CONDA_ENV% && python -m Cliente.mainClient && pause"

endlocal
