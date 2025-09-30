# ejecutar haciendo (bash):
# $ chmod +x run.sh
# $ ./run.sh

#!/bin/bash

# Ejecutar Nodo 1 en background
python main.py 1 10001 1:10001,2:10002,3:10003 & # background 

# Ejecutar Nodo 2 en background
python main.py 2 10002 1:10001,2:10002,3:10003 &

# Ejecutar Nodo 3 en background
python main.py 3 10003 1:10001,2:10002,3:10003 &

# Esperar a que todos terminen (opcional)
wait
