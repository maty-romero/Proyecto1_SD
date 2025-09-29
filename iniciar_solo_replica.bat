@echo off
setlocal

REM === CONFIGURACIÓN ===
set "CONDA_ENV=base"
set "PROYECTO_DIR=C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1"
set "CONDA_ACTIVATE=C:\ProgramData\Miniconda3\Scripts\activate.bat"

REM Cambiar al directorio del proyecto
cd /d "%PROYECTO_DIR%"

REM Iniciar una réplica
start "Replica" cmd /k "call "%CONDA_ACTIVATE%" %CONDA_ENV% && python -m Servidor.mainReplicaLimpio && pause"

endlocal
