@echo off
set CONDA_ENV=base

REM Ruta del proyecto
cd /d "C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1"

echo Iniciando replicas de forma escalonada...

REM Iniciar Replica-1 (sin delay)
echo Iniciando Replica-1...
start "Replica-1" cmd /k "C:\ProgramData\Miniconda3\Scripts\activate.bat && conda activate %CONDA_ENV% && python -m Servidor.mainReplica"

REM Iniciar Replica-2 (con delay de 5 segundos)
echo Iniciando Replica-2 (esperará 5 segundos)...
start "Replica-2" cmd /k "timeout /t 5 /nobreak >nul && C:\ProgramData\Miniconda3\Scripts\activate.bat && conda activate %CONDA_ENV% && python -m Servidor.mainReplica"

REM Iniciar Replica-3 (con delay de 10 segundos)
echo Iniciando Replica-3 (esperará 10 segundos)...
start "Replica-3" cmd /k "timeout /t 10 /nobreak >nul && C:\ProgramData\Miniconda3\Scripts\activate.bat && conda activate %CONDA_ENV% && python -m Servidor.mainReplica"

echo Todas las replicas han sido iniciadas.
pause