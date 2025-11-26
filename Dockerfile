FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    ARCH_FRONTEND=noninteractive \
    DISPLAY=:0

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libv4l-dev \
    v4l-utils \
    python3-tk \
    tk-dev \
    libsdl2-mixer-2.0-0 \
    libsdl2-2.0-0 \
    alsa-utils \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p output models data

RUN chmod +x start_*.py capture_for_blender.sh 2>/dev/null || true

EXPOSE 5000


CMD ["python", "start_main.py"]
