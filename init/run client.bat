@echo off
echo Iniciando nodos...

REM Nos aseguramos de estar en la raíz del proyecto (subimos un nivel desde init si el .bat está ahí)
cd /d "%~dp0.."

start "Cliente" cmd /k "python -m init.mainClient"
