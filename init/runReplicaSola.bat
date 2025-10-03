@echo off
echo Iniciando nodos...

REM Nos aseguramos de estar en la raíz del proyecto (subimos un nivel desde init si el .bat está ahí)
cd /d "%~dp0.."

::MODIFICAR EL VALOR 1 ANTES DE & AL NODO CORRESPONDIENTE
start "Nodo replica" cmd /k "python -m init.mainZC 1 & pause"

echo Todos los nodos fueron iniciados.
pause
