FROM python:3.11-slim

# Instalar FFmpeg y dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/database data/downloads data/processed logs

# Dar permisos
RUN chmod +x scripts/*.py

# Healthcheck
HEALTHCHECK --interval=1h --timeout=10s \
  CMD python -c "import sqlite3; sqlite3.connect('data/database/videos.db').close()" || exit 1

CMD ["python", "scripts/run_daily.py"]
