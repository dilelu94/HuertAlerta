import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables locales si existen
load_dotenv()

def send_telegram_photo(token, chat_id, photo_path, caption):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    # Si la ruta es un archivo local
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            payload = {
                'chat_id': chat_id,
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, data=payload, files=files)
    else:
        # Si por alguna razón sigue siendo una URL o no existe el archivo
        payload = {
            "chat_id": chat_id,
            "photo": photo_path,
            "caption": caption,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
    
    return response.json()

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def main():
    current_month = datetime.now().month
    months_es = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    month_name = months_es[current_month]
    
    with open('seeds.json', 'r', encoding='utf-8') as f:
        seeds = json.load(f)
    
    plantable_seeds = [
        s for s in seeds 
        if current_month in s['planting_months'] and s['stock'] > 0
    ]
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("Error: Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")
        return

    if not plantable_seeds:
        send_telegram_message(token, chat_id, f"🌱 *Huerto Notificador*\n\nNo hay semillas en stock para plantar en {month_name}.")
        return

    # Mensaje de cabecera
    header = f"🌱 *¡Es viernes de siembra!*\nMes: {month_name}\n\nAquí tienes las recomendaciones de la semana:"
    send_telegram_message(token, chat_id, header)

    # Enviar cada semilla con su foto
    for s in plantable_seeds:
        # Evitar redundancia si la familia ya está en el nombre (ej: Medicinales)
        family_display = f" ({s['family']})" if s['family'].lower() not in s['name'].lower() else ""
        
        caption = (
            f"🌿 *{s['name']}*{family_display}\n"
            f"🕒 *Cosecha:* ~{s['harvest_days']} días\n"
            f"📦 *Stock:* {s['stock']} unidades\n"
            f"⚠️ *Desplante:* {s['removal_type']}\n"
            f"📝 _'{s['observations']}'_"
        )
        # Usar image_path si existe, sino fallback a image_url
        img_source = s.get('image_path') or s.get('image_url')
        if img_source:
            send_telegram_photo(token, chat_id, img_source, caption)
        else:
            send_telegram_message(token, chat_id, caption)

if __name__ == "__main__":
    main()
