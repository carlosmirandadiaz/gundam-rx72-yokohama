import os
from flask import Flask, request, jsonify, render_template
import openai
import json
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Obtiene la API Key desde las variables de entorno
api_key = os.getenv("OPENAI_API_KEY")

# Verifica si la API Key está definida
if not api_key:
    raise ValueError("La API Key de OpenAI no está configurada. Asegúrate de agregarla en Railway.")

# Crear cliente OpenAI con la API Key
client = openai.OpenAI(api_key=api_key)

def traducir_a_japones(texto):
    """
    Traduce una palabra o frase en español a japonés, incluyendo hiragana, romanji, traducción y pronunciación.
    
    Parámetros:
        texto (str): La palabra o frase en español que se desea traducir.

    Retorna:
        dict: Un diccionario con la traducción en formato JSON o un mensaje de error.
    """
    # Definir el prompt con instrucciones claras y ejemplos
    prompt = f"""
    Traduce la siguiente palabra o frase en español a japonés, incluyendo hiragana, romanji, traducción y pronunciación. 
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

    3. **Formato de respuesta JSON**:
       {{
           "hiragana": "Texto en hiragana",
           "romanji": "Transliteración en romanji",
           "traduccion": "Traducción en español",
           "pronunciacion": "Pronunciación en romanji"
       }}

    4. **Precisión**:
       - No agregues explicaciones adicionales. Devuelve **EXCLUSIVAMENTE JSON válido**.

    **Palabra/frase a traducir:** "{texto}"
    """

    try:
        # Llamar a la API de OpenAI
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un traductor experto en japonés. Devuelve únicamente JSON válido sin explicaciones."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extraer el contenido de la respuesta
        contenido = respuesta.choices[0].message.content.strip()
        print("Respuesta de OpenAI:", contenido)  # Para depuración

        # Verificar si la respuesta es un JSON válido
        json_respuesta = json.loads(contenido)
        return json_respuesta

    except openai.OpenAIError as e:
        # Manejar errores de la API de OpenAI
        print(f"Error en OpenAI: {e}")
        return {"error": f"Error en OpenAI: {str(e)}"}

    except json.JSONDecodeError:
        # Manejar errores de decodificación JSON
        print("Error al convertir la respuesta en JSON")
        return {"error": "La respuesta de OpenAI no es un JSON válido. Intenta de nuevo."}

    except Exception as e:
        # Manejar cualquier otro error inesperado
        print(f"Error inesperado: {e}")
        return {"error": f"Error inesperado: {str(e)}"}

# Ruta para servir el frontend
@app.route("/")
def index():
    return render_template("index.html")

# Ruta para procesar la traducción
@app.route("/traducir", methods=["POST"])
def traducir():
    datos = request.json
    texto = datos.get("texto", "")
    if not texto:
        return jsonify({"error": "Texto vacío"}), 400

    resultado = traducir_a_japones(texto)
    print("Respuesta enviada al frontend:", resultado)
    return jsonify(resultado)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
