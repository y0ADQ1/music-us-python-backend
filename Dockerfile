# Usamos Python oficial ligero
FROM python:3.11-slim-bookworm

# Instalamos FFmpeg (El motor de conversión de audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app

# Copiamos primero dependencias para optimizar caché
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el resto del código (incluyendo el cookies.txt)
COPY . .

# Exponemos el puerto
EXPOSE 10000

# Usamos la variable $PORT que Render nos inyecta automáticamente
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app
