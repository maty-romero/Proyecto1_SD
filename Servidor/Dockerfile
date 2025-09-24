FROM mongo:8.0.14-noble

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Instalar Python y pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    libssl-dev \
    libffi-dev \
    wget \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Copiar proyecto entero (IMPORTANTE: contexto = raíz Proyecto1_SD)
COPY ../ /app/

# Instalar dependencias Python
RUN pip3 install --no-cache-dir --break-system-packages -r ./Servidor/requirements.txt

# Crear directorio de datos de MongoDB
RUN mkdir -p /data/db && chown -R mongodb:mongodb /data/db

# Copiar entrypoint
COPY ./Servidor/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puertos
EXPOSE 27017 9090

ENTRYPOINT ["/entrypoint.sh"]
