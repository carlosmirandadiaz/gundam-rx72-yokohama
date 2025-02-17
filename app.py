import os
from flask import Flask, request, jsonify, render_template, send_file
import openai
import json
from flask_cors import CORS
import requests
from io import BytesIO
import time
import threading
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Obtiene la API Key desde las variables de entorno
api_key = os.getenv("OPENAI_API_KEY")

# Verifica si la API Key está definida
if not api_key:
    raise ValueError("La API Key de OpenAI no está configurada. Asegúrate de agregarla en Railway.")

# Crear cliente OpenAI con la API Key
client = openai.OpenAI(api_key=api_key)

# Diccionario para almacenar los archivos de audio y su tiempo de expiración
audio_files = {}

def eliminar_archivo_audio(audio_path):
    """
    Elimina un archivo de audio después de 5 minutos.
    """
    time.sleep(300)  # Esperar 5 minutos (300 segundos)
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"Archivo {audio_path} eliminado.")
    if audio_path in audio_files:
        del audio_files[audio_path]

def traducir_a_japones(texto):
    """
    Traduce una palabra o frase en español a japonés, incluyendo hiragana, romanji, traducción y una guía fonética.
    
    Parámetros:
        texto (str): La palabra o frase en español que se desea traducir.

    Retorna:
        dict: Un diccionario con la traducción en formato JSON o un mensaje de error.
    """
    # Definir el prompt con instrucciones claras y ejemplos
    prompt = f"""
    Traduce la siguiente palabra o frase en español a japonés, incluyendo hiragana, romanji, traducción y una guía fonética para pronunciar correctamente el hiragana.
    Devuelve el resultado en formato JSON.

    **Reglas importantes:**
    1. **Contexto y naturalidad**: 
       - Asegúrate de que la traducción sea precisa y adecuada al contexto.
       - Si hay varias formas en japonés, usa la más común en una conversación estándar.

    2. **Saludos y expresiones**:
       - Si la palabra es un saludo o expresión, usa la traducción más natural:
         - "Hola" → こんにちは (konnichiwa)
         - "Perdón" → ごめんなさい (gomen nasai)
         - "Lo siento" → すみません (sumimasen)

    3. **Guía fonética**:
       - Proporciona una guía fonética en español para ayudar a pronunciar el hiragana.
       - Ejemplo: こんにちは → "Koh-nnee-chee-wah"

    4. **Formato de respuesta JSON**:
       {{
           "hiragana": "Texto en hiragana",
           "romanji": "Transliteración en romanji",
           "traduccion": "Traducción en español",
           "pronunciacion": "Guía fonética en español"
       }}

    5. **Precisión**:
       - No agregues explicaciones adicionales. Devuelve **EXCLUSIVAMENTE JSON válido**.

    **Palabra/frase a traducir:** "{texto}"
    """

    try:
        # Llamar a la API de OpenAI usando el nuevo formato
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un traductor experto en japonés. Devuelve únicamente JSON válido sin explicaciones."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extraer el contenido de la respuesta
        contenido = respuesta.choices[0].message.content.strip()
        print("Respuesta de OpenAI:", contenido)  # Para depuración

        # Preprocesar la respuesta para eliminar ```json``` o cualquier texto no deseado
        if contenido.startswith("```json") and contenido.endswith("```"):
            contenido = contenido[7:-3].strip()  # Eliminar ```json y las triples comillas

        # Verificar si la respuesta es un JSON válido
        json_respuesta = json.loads(contenido)
        return json_respuesta

    except json.JSONDecodeError:
        # Manejar errores de decodificación JSON
        print("Error: La respuesta de OpenAI no es un JSON válido.")
        return {"error": "La respuesta de OpenAI no es un JSON válido. Intenta de nuevo."}

    except Exception as e:
        # Manejar errores de la API de OpenAI o cualquier otro error
        print(f"Error: {e}")
        return {"error": f"Error: {str(e)}"}

def generar_audio(texto_japones, voz="alloy"):
    """
    Genera un archivo de audio a partir de un texto en japonés usando la API de OpenAI TTS.

    Parámetros:
        texto_japones (str): El texto en japonés que se convertirá en audio.
        voz (str): La voz a utilizar. Opciones: "alloy", "echo", "fable", "onyx", "nova", "shimmer".

    Retorna:
        BytesIO: Un objeto BytesIO con el archivo de audio en formato MP3.
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voz,
            input=texto_japones
        )

        # Guardar el audio en un objeto BytesIO
        audio_buffer = BytesIO()
        response.stream_to_file(audio_buffer)
        audio_buffer.seek(0)  # Rebobinar el buffer para que pueda ser leído
        return audio_buffer

    except Exception as e:
        print(f"Error al generar audio: {e}")
        return None

# Ruta para servir el frontend
@app.route("/")
def index():
    return render_template("index.html")

# Ruta para procesar la traducción y generar audio
@app.route("/traducir", methods=["POST"])
def traducir():
    datos = request.json
    texto = datos.get("texto", "")
    if not texto:
        return jsonify({"error": "Texto vacío"}), 400

    # Traducir el texto
    resultado = traducir_a_japones(texto)
    if "error" in resultado:
        return jsonify(resultado), 400

    # Generar audio a partir del texto en hiragana
    audio_buffer = generar_audio(resultado["hiragana"])
    if not audio_buffer:
        return jsonify({"error": "Error al generar el audio"}), 500

    # Guardar el archivo de audio temporalmente
    audio_path = f"static/audio/{int(time.time())}.mp3"  # Nombre único basado en el timestamp
    with open(audio_path, "wb") as f:
        f.write(audio_buffer.getvalue())

    # Programar la eliminación del archivo después de 5 minutos
    threading.Thread(target=eliminar_archivo_audio, args=(audio_path,)).start()

    # Devolver la respuesta con la URL del archivo de audio
    resultado["audio_url"] = f"/{audio_path}"
    print("Respuesta enviada al frontend:", resultado)
    return jsonify(resultado)

# Ruta para servir el archivo de audio
@app.route("/static/audio/<filename>")
def servir_audio(filename):
    audio_path = f"static/audio/{filename}"
    if not os.path.exists(audio_path):
        return jsonify({"error": "El archivo de audio ha expirado. Por favor, realiza una nueva búsqueda."}), 404
    return send_file(audio_path, mimetype="audio/mpeg")

if __name__ == "__main__":
    # Crear la carpeta de audio si no existe
    os.makedirs("static/audio", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)