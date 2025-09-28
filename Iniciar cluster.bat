@echo off
set CONDA_ENV=base

REM Ruta del proyecto
cd /d "C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1"

start "NameServer" cmd /k "call conda activate %CONDA_ENV% && python -m ServidorNombres.mainNameServer"

echo Creando scripts auxiliares...

REM Crear script para Replica-1 (sin delay)
echo @echo off > replica1.bat
echo cd /d "C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1" >> replica1.bat
echo call C:\ProgramData\Miniconda3\Scripts\activate.bat >> replica1.bat
echo call conda activate %CONDA_ENV% >> replica1.bat
echo python -m Servidor.mainReplica >> replica1.bat
echo pause >> replica1.bat

REM Crear script para Replica-2 (delay 5s)
echo @echo off > replica2.bat
echo echo Esperando 5 segundos antes de iniciar Replica-2... >> replica2.bat
echo timeout /t 5 /nobreak ^>nul >> replica2.bat
echo cd /d "C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1" >> replica2.bat
echo call C:\ProgramData\Miniconda3\Scripts\activate.bat >> replica2.bat
echo call conda activate %CONDA_ENV% >> replica2.bat
echo python -m Servidor.mainReplica >> replica2.bat
echo pause >> replica2.bat

REM Crear script para Replica-3 (delay 10s)
echo @echo off > replica3.bat
echo echo Esperando 10 segundos antes de iniciar Replica-3... >> replica3.bat
echo timeout /t 10 /nobreak ^>nul >> replica3.bat
echo cd /d "C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1" >> replica3.bat
echo call C:\ProgramData\Miniconda3\Scripts\activate.bat >> replica3.bat
echo call conda activate %CONDA_ENV% >> replica3.bat
echo python -m Servidor.mainReplica >> replica3.bat
echo pause >> replica3.bat

echo Iniciando replicas...

REM Iniciar cada replica usando su script auxiliar
start "Replica-1" replica1.bat
start "Replica-2" replica2.bat
start "Replica-3" replica3.bat

echo Todas las replicas han sido lanzadas.
echo Los archivos auxiliares (replica1.bat, replica2.bat, replica3.bat) se pueden borrar después.
pause