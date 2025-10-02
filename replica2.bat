@echo off 
echo Esperando 5 segundos antes de iniciar Replica-2... 
timeout /t 5 /nobreak >nul 
cd /d "C:\Users\Hans\Documents\Github\Universidad\Proyecto1_SD" 
call C:\ProgramData\Miniconda3\Scripts\activate.bat 
call conda activate base 
python -m Servidor.mainReplica 
pause 
