FROM python:3.9-slim

# 1. Establecemos /app como raíz de la aplicación
WORKDIR /ServidorNombres

# 2. Copiamos TODO el proyecto (porque el contexto es la raíz)
COPY . ./ServidorNombres

# 3. Instalamos Pyro5
RUN pip install --no-cache-dir Pyro5

# 4. Exponemos el puerto del NameServer
EXPOSE 9090 9091

# 5a. OPCIÓN A: Ejecutar como módulo (requiere __init__.py en ServidorNombres/)
# Asegúrate de que el archivo se llama exactamente mainNameServer.py
CMD ["python", "-m", "ServidorNombres.mainNameServer"]

# 5b. OPCIÓN B: Ejecutar directamente el script
# CMD ["python3", "ServidorNombres/mainNameServer.py"]
