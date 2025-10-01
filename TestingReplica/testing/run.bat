@echo off
echo Iniciando nodos...


start "Nodo 1" cmd /k "python main.py 1 10001 1:10001,2:10002,3:10003,4:10004,5:10005 False & echo Presiona una tecla para cerrar... &"
start "Nodo 2" cmd /k "python main.py 2 10002 1:10001,2:10002,3:10003,4:10004,5:10005 False & echo Presiona una tecla para cerrar... &"
start "Nodo 3" cmd /k "python main.py 3 10003 1:10001,2:10002,3:10003,4:10004,5:10005 False & echo Presiona una tecla para cerrar... &"
start "Nodo 4" cmd /k "python main.py 4 10004 1:10001,2:10002,3:10003,4:10004,5:10005 False & echo Presiona una tecla para cerrar... &"
start "Nodo 5" cmd /k "python main.py 5 10005 1:10001,2:10002,3:10003,4:10004,5:10005 True & echo Presiona una tecla para cerrar... & pause"
