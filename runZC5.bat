@echo off
call C:\Users\Hans\miniconda3\Scripts\activate.bat base
cd /d C:\Users\Hans\Documents\Github\Universidad\Proyecto1_SD

start "Nodo 1" cmd /k "python -m init.mainZC 1"
start "Nodo 2" cmd /k "python -m init.mainZC 2"
start "Nodo 3" cmd /k "python -m init.mainZC 3"

echo Todos los nodos fueron iniciados.
pause