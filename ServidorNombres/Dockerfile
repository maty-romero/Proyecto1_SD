FROM python:3.9-slim

WORKDIR /app

COPY ./mainNameServer.py /app/
COPY ./Servidor /app/Servidor
COPY ./utils /app/utils  # si tenés helpers

RUN pip install --no-cache-dir Pyro5

EXPOSE 9090

CMD ["python3", "mainNameServer.py"]
