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

# Usamos Gunicorn para correr la app de forma estable en la nube, con un timeout alto (120s) por si la canción es larga
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app:app"]