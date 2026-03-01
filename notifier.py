import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables locales si existen
load_dotenv()

def send_telegram_photo(token, chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
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
        send_telegram_message(token, chat_id, "🌱 *Huerto Notificador*\n\nNo hay semillas en stock para plantar este mes.")
        return

    # Mensaje de cabecera
    header = f"🌱 *¡Es viernes de siembra!*\nMes: {datetime.now().strftime('%B')}\n\nAquí tienes las recomendaciones de hoy:"
    send_telegram_message(token, chat_id, header)

    # Enviar cada semilla con su foto
    for s in plantable_seeds:
        caption = (
            f"🌿 *{s['name']}* ({s['family']})\n"
            f"🕒 *Cosecha:* ~{s['harvest_days']} días\n"
            f"📦 *Stock:* {s['stock']} unidades\n"
            f"⚠️ *Desplante:* {s['removal_type']}\n"
            f"📝 _'{s['observations']}'_"
        )
        send_telegram_photo(token, chat_id, s['image_url'], caption)

if __name__ == "__main__":
    main()
