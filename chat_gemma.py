import json
import os
import sys
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    sys.exit("Falta GEMINI_API_KEY.")

MODEL = "gemma-4-31b-it"
ARCHIVO = "historial.json"
ROL = ("Eres un asistente útil. Responde en español. "
       "Si falta información para responder bien, pregunta antes de asumir.")

client = genai.Client(api_key=API_KEY)


def cargar():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, encoding="utf-8") as f:
            return json.load(f)
    return []


def guardar(historial):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)


def a_contents(historial):
    return [
        types.Content(role=m["rol"], parts=[types.Part.from_text(text=m["texto"])])
        for m in historial
    ]


def main():
    historial = cargar()
    print(f"Chat con {MODEL}")
    print("Comandos: 'nuevo' borra la memoria | '/archivo ruta' adjunta un archivo | 'salir' termina")
    if historial:
        print(f"(Se cargaron {len(historial)} mensajes previos)")

    while True:
        pregunta = input("\nTú: ").strip()
        if not pregunta:
            continue
        if pregunta.lower() == "salir":
            break
        if pregunta.lower() == "nuevo":
            historial = []
            guardar(historial)
            print("Memoria borrada.")
            continue

        if pregunta.startswith("/archivo "):
            ruta = pregunta[len("/archivo "):].strip().strip('"')
            try:
                with open(ruta, encoding="utf-8") as f:
                    contenido = f.read()
            except Exception as e:
                print(f"[No pude leer el archivo: {e}]")
                continue
            consulta = input("¿Qué quieres saber o cambiar de este archivo?: ").strip()
            pregunta = (f'Este es mi archivo "{os.path.basename(ruta)}":\n\n'
                        f"{contenido}\n\n{consulta}")

        historial.append({"rol": "user", "texto": pregunta})
        try:
            r = client.models.generate_content(
                model=MODEL,
                contents=a_contents(historial),
                config=types.GenerateContentConfig(system_instruction=ROL),
            )
        except Exception as e:
            historial.pop()
            print(f"[Error: {e}]")
            continue

        respuesta = r.text
        if not respuesta:
            historial.pop()
            print("[El modelo no devolvió texto. Intenta reformular la pregunta.]")
            continue

        historial.append({"rol": "model", "texto": respuesta})
        guardar(historial)
        print(f"\nGemma: {respuesta}")


if __name__ == "__main__":
    main()