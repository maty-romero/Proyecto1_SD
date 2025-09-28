@echo off
set CONDA_ENV=base
start "NameServer" cmd /k "call conda activate %CONDA_ENV% && python -m ServidorNombres.mainNameServer"
