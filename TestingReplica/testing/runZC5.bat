@echo off
echo Iniciando nodos...

REM Nos aseguramos de estar en la raíz del proyecto (subimos un nivel desde init si el .bat está ahí)
cd /d "%~dp0.."

start "Servidor de Nombres" cmd /k "python -m init.mainNameServer"
start "Nodo 1" cmd /k "python -m init.mainZC 1 & pause"
start "Nodo 2" cmd /k "python -m init.mainZC 2 & pause"
start "Nodo 3" cmd /k "python -m init.mainZC 3 & pause"
start "Nodo 4" cmd /k "python -m init.mainZC 4 & pause"
start "Nodo 5" cmd /k "python -m init.mainZC 5 & pause"

