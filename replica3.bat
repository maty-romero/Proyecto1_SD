@echo off 
echo Esperando 10 segundos antes de iniciar Replica-3... 
timeout /t 10 /nobreak >nul 
cd /d "C:\Users\Elías\OneDrive\UNIVERSIDAD 2025\2do Cuatrimestre\Sistemas Distribuidos\Repositorio\Tutti Frutti\Proyecto1_SD-1" 
call C:\ProgramData\Miniconda3\Scripts\activate.bat 
call conda activate base 
python -m Servidor.mainReplica 
pause 
