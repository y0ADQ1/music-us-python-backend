from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import time
import io

app = Flask(__name__)
# Permite peticiones desde tu app de React Native
CORS(app)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"message": "API de descarga en Python funcionando al 100%"})

@app.route('/api/download-audio', methods=['GET'])
def download_audio():
    # Recibimos la URL por método GET igual que en tu app
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "Debes de proporcionar una URL válida"}), 400

    file_name = f"audio_{int(time.time())}"
    output_template = os.path.join(TEMP_DIR, f"{file_name}.%(ext)s")
    final_file_path = os.path.join(TEMP_DIR, f"{file_name}.mp3")

    print(f"Iniciando descarga de audio para URL: {url}")

    # Forzamos la ruta absoluta al archivo de cookies
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(base_dir, 'cookies.txt')

    # Configuración nativa de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best', # Volvemos a pedir solo audio
        'outtmpl': output_template,
        'cookiefile': cookie_path, 
        
        # 👇 El truco maestro en Python para evitar el 403 de YouTube 👇
        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        },
        
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # Ejecutamos la descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(final_file_path):
            return jsonify({"error": "Error al procesar el archivo descargado"}), 500

        # Leemos el archivo MP3 a la memoria RAM
        with open(final_file_path, 'rb') as f:
            audio_data = f.read()

        # ¡Magia de Python! Eliminamos el archivo físico INMEDIATAMENTE
        os.remove(final_file_path)

        # Enviamos el audio directamente desde la memoria a tu celular
        return send_file(
            io.BytesIO(audio_data),
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="audio_descargado.mp3"
        )

    except Exception as e:
        print(f"Error durante la descarga: {str(e)}")
        return jsonify({
            "error": "Error al procesar el enlace. Verifica que el video exista.",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    # Esto solo se usa si lo corres localmente en tu PC
    app.run(host='0.0.0.0', port=3000, debug=True)
