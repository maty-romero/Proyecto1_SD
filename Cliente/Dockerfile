FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    QT_X11_NO_MITSHM=1

WORKDIR /Cliente

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    libxcb-xinerama0 \
    libpulse0 \
    libxkbcommon0 \
    x11-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    x11-xserver-utils \
    freeglut3-dev \
  && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . ./Cliente

ENTRYPOINT [ "bash", "-c", "xhost +local:docker || true && python -m Cliente.mainClient" ]

