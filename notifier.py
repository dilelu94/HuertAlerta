import json
import os
import requests
import time
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

import unicodedata
import re

def slugify(text):
    text = unicodedata.normalize('NFD', text.lower())
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text

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

    # Mensaje de cabecera con enlaces a la ficha de cada planta en GitHub Pages
    base_url = "https://dilelu94.github.io/HuertAlerta/#p"
    lines = []
    for s in plantable_seeds:
        seed_id = s.get('id') or slugify(s['name'])
        url = f"{base_url}{seed_id}"
        lines.append(f"• [{s['name']}]({url})")

    seed_list_text = "\n".join(lines)
    header = (
        f"🌱 *¡Es viernes de siembra!*\n"
        f"Mes: *{month_name}*\n\n"
        f"*Lo que puedes sembrar ahora ({len(plantable_seeds)} variedades):*\n\n"
        f"{seed_list_text}\n\n"
        f"👉 _Toca el nombre de cualquier planta para ver su foto, cosecha y tips._"
    )
    send_telegram_message(token, chat_id, header)

if __name__ == "__main__":
    main()
