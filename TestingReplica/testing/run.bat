@echo off
echo Iniciando nodos...

start "Nodo 1" python main.py 1 10001 1:10001,2:10002,3:10003
start "Nodo 2" python main.py 2 10002 1:10001,2:10002,3:10003
start "Nodo 3" python main.py 3 10003 1:10001,2:10002,3:10003

echo Todos los nodos han sido iniciados en ventanas separadas.
pause