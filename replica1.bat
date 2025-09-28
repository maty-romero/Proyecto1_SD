@echo off 
cd /d "C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1" 
call C:\ProgramData\Miniconda3\Scripts\activate.bat 
call conda activate base 
python -m Servidor.mainReplica 
pause 
