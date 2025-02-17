import os
from flask import Flask, request, jsonify
import openai
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configura tu API Key de OpenAI
openai.api_key = "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"

def traducir_a_japones(texto):
    prompt = f"Convierte '{texto}' a Hiragana, Romanji y Español con pronunciación en Romanji. Devuelve SOLO un JSON válido con las claves 'hiragana', 'romanji', 'traduccion', 'pronunciacion'."

    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un traductor experto en japonés. Devuelve únicamente JSON válido."},
            {"role": "user", "content": prompt}
        ]
    )

    contenido = respuesta["choices"][0]["message"]["content"]
    print("Respuesta de OpenAI:", contenido)  # Para depuración

    try:
        # Convierte la respuesta en un objeto JSON válido
        json_respuesta = json.loads(contenido.replace("'", '"'))  
        return json_respuesta
    except json.JSONDecodeError:
        print("Error al convertir la respuesta en JSON")
        return {"error": "La respuesta de OpenAI no es un JSON válido"}

@app.route("/traducir", methods=["POST"])
def traducir():
    datos = request.json
    texto = datos.get("texto", "")
    if not texto:
        return jsonify({"error": "Texto vacío"}), 400

    resultado = traducir_a_japones(texto)
    print("Respuesta enviada al frontend:", resultado)  # Depuración
    return jsonify(resultado)  # Ahora enviamos JSON real

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Obtiene el puerto de Railway o usa 5000 como fallback
    app.run(host="0.0.0.0", port=port)

    