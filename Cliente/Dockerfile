FROM python:3.9-slim

# 1) Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    QT_X11_NO_MITSHM=1

# 2) Directorio de trabajo
WORKDIR /Cliente

# 3) Dependencias de sistema para PyQt6 + X11 (xhost)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb-xinerama0 \
    libpulse0 \
    libxkbcommon0 \
    x11-utils \
  && rm -rf /var/lib/apt/lists/*

# 5) Copiar el código del cliente
COPY . ./Cliente

# 4) Instalar dependencias Python
RUN pip install --no-cache-dir -r ./Cliente/requirements.txt

# 6) Exponer ningún puerto (es GUI), pero dejamos la red para Pyro5
#    no hace falta EXPOSE X11, usamos el socket
# EXPOSE 9092      # si tu cliente abre puertos, agregalos aquí

# 7) Entrypoint: primero habilita el acceso X, luego arranca tu GUI
ENTRYPOINT [ "bash", "-c", "\
    xhost +local:docker || true && \
    python3 -m Cliente.main" ]
