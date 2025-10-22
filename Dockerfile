FROM python:3.11-slim

WORKDIR /app

# Copiar requirements y aprovechar cache
COPY requirements.txt /app/requirements.txt

# Dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        chromium \
        chromium-driver \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código
COPY . /app

# Variables para Selenium/Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="/usr/bin/:${PATH}"

ENV PYTHONPATH=/app/src
# Ejecutar el módulo principal bajo src
ENTRYPOINT ["python", "-m", "src.main"]
