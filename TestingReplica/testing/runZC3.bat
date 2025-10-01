@echo off
echo Iniciando nodos...
start "Nodo 1" cmd /k "python mainZC.py 1 & pause"
start "Nodo 2" cmd /k "python mainZC.py 2 & pause"
start "Nodo 3" cmd /k "python mainZC.py 3 & pause"