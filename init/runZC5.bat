@echo off
echo Iniciando nodos...

start "Nodo 1" cmd /k "python -m Init.mainZC 1 & pause"
start "Nodo 2" cmd /k "python -m Init.mainZC 2 & pause"
start "Nodo 3" cmd /k "python -m Init.mainZC 3 & pause"
::start "Nodo 4" cmd /k "python mainZC.py 4 & pause"
::start "Nodo 5" cmd /k "python mainZC.py 5 & pause"


echo Todos los nodos fueron iniciados.
pause
