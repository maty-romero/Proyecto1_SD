#!/bin/bash
set -e

# Iniciar mongod en segundo plano
mongod --bind_ip_all --replSet rs0 --dbpath /data/db --logpath /var/log/mongod.log &

# Esperar a que mongod esté listo
until mongosh --quiet --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
  echo "Esperando a que MongoDB inicie..."
  sleep 2
done

echo "MongoDB iniciado."

# Ejecutar tu servidor Python en primer plano
exec python3 -m Servidor.mainServer
