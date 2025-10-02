@echo off
set CONDA_ENV=base

cd /d "C:\Users\Hans\Documents\Github\Universidad\Proyecto1_SD"

start "NameServer" cmd /k "call C:\Users\Hans\miniconda3\Scripts\activate.bat %CONDA_ENV% && python -m ServidorNombres.mainNameServer"
