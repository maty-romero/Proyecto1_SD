FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    QT_X11_NO_MITSHM=1 \
    QT_QPA_PLATFORM=offscreen \
    QTWEBENGINE_DISABLE_SANDBOX=1 

WORKDIR /Cliente

# RUN apt-get update && apt-get install -y \
#     libgl1 \
#     libglx-mesa0 \
#     libglib2.0-0 \
#     libxcb-xinerama0 \
#     libpulse0 \
#     libxkbcommon0 \
#     x11-utils \
#     ffmpeg \
#     libsm6 \
#     libxext6 \
#     x11-xserver-utils \
#     freeglut3-dev \
#   && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    libpulse0 \
    libxkbcommon0 \
    libegl1 \
    libgles2 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxrandr2 \
    libxfixes3 \
    libxcursor1 \
    libxcb1 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-shm0 \
    libxcb-util1 \
    x11-utils \
    ffmpeg \
    freeglut3-dev \
    libxcb-cursor-dev \ 
  && rm -rf /var/lib/apt/lists/*

# Copiar el resto del código
COPY . ./Cliente

CMD ["python", "-m", "Cliente.mainClient"]
