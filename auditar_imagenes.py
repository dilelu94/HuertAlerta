import base64
import glob
import json
import os
import sys
import time
import urllib.request
import urllib.error

# Cargar API Keys
KEYS_PATH = "/home/dilelu/repos/Api keys Gemini.txt"
with open(KEYS_PATH, "r", encoding="utf-8") as f:
    RAW_KEYS = [line.strip() for line in f if line.strip()]

API_KEYS = [k for k in RAW_KEYS if not (k.endswith("SqbtAg") or k.endswith("6QUbFQ") or k.endswith("wdSuXg"))]
print(f"[*] Usando {len(API_KEYS)} API keys válidas de Gemini en rotación.")

# gemini-2.5-flash y gemini-3.5-flash son los que responden en 2 segundos
MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-3.5-flash"]
IMAGES_DIR = "/home/dilelu/repos/HuertAlerta/images"
OUTPUT_REPORT = "/home/dilelu/repos/HuertAlerta/reporte_auditoria_imagenes.json"

image_files = sorted(glob.glob(os.path.join(IMAGES_DIR, "*.*")))
image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

print(f"[*] Analizando {len(image_files)} imágenes para huerta hogareña...\n")

PROMPT = """Eres un agrónomo experto en huertas familiares y hogareñas.
Analiza con rigor crítico esta imagen que pertenece al catálogo visual de una app para huerteros.

Evalúa:
1. ¿La imagen es verdaderamente representativa de la planta viva en una huerta hogareña?
2. ¿Un principiante puede deducir el porte/estructura real (porte rastrero, trepador, mata, altura aproximada)?
3. ¿Ayuda a entender visualmente cómo cosecharla o cómo crece (hojas sueltas, fruto, raíz, penca)?
4. ¿Presenta defectos notables? (ej: collage confuso de varias especies juntas, plato de comida, solo semillas, borrosa o recortada).
5. Calificación técnica de 1 a 10.
6. Veredicto: 'MANTENER' (si es excelente), 'MEJORABLE' (si zafa pero podría ser más clara), o 'REEMPLAZAR' (si confunde, si es un collage de múltiples especies o no muestra la planta viva).
7. Recomendación específica de qué tipo de toma o foto convendría tener.

Responde obligatoriamente en formato JSON válido con la siguiente estructura:
{
  "representativa_huerta": true,
  "claridad_porte_estructura": "comentario breve",
  "utilidad_para_cosecha": "comentario breve",
  "defectos_observados": "comentario breve o 'Ninguno'",
  "puntuacion": 8,
  "veredicto": "MANTENER",
  "recomendacion": "comentario claro"
}
"""

results = []
key_index = 0

for idx, img_path in enumerate(image_files, 1):
    filename = os.path.basename(img_path)
    print(f"[{idx:02d}/{len(image_files)}] {filename:<45}", end=" ", flush=True)

    mime_type = "image/jpeg"
    if filename.lower().endswith(".png"):
        mime_type = "image/png"
    elif filename.lower().endswith(".webp"):
        mime_type = "image/webp"

    with open(img_path, "rb") as f:
        img_bytes = f.read()
    b64_img = base64.b64encode(img_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Archivo: {filename}\n{PROMPT}"},
                    {"inline_data": {"mime_type": mime_type, "data": b64_img}}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }
    req_data = json.dumps(payload).encode("utf-8")

    success = False

    for model_name in MODELS_TO_TRY:
        if success:
            break
        current_key = API_KEYS[key_index]
        key_index = (key_index + 1) % len(API_KEYS)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={current_key}"
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                text_content = resp_data["candidates"][0]["content"]["parts"][0]["text"]
                eval_data = json.loads(text_content)
                eval_data["archivo"] = filename
                eval_data["modelo_usado"] = model_name
                results.append(eval_data)
                print(f"-> {eval_data.get('veredicto'):<10} ({eval_data.get('puntuacion')}/10)")
                success = True
                break
        except Exception as e:
            time.sleep(1)

    if not success:
        print("-> [ERROR]")

    # Pausa de 1.2 segundos para mantener el ritmo suave y rotar keys
    time.sleep(1.2)

with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n[✓] ¡Auditoría completa terminada con éxito! Guardada en {OUTPUT_REPORT}")
