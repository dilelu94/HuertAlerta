import json
import logging
import os
import re
import sys
import time
import unicodedata
import requests

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("HuertAlertaBot")

def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

class HuertAlertaBot:
    def __init__(self, token: str, authorized_chat_ids: list[str], repo_dir: str):
        self.token = token
        self.authorized_chat_ids = set(str(cid) for cid in authorized_chat_ids if cid)
        self.repo_dir = repo_dir
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self.seeds = []
        self.load_seeds()

    def load_seeds(self):
        seeds_path = os.path.join(self.repo_dir, "seeds.json")
        try:
            with open(seeds_path, "r", encoding="utf-8") as f:
                self.seeds = json.load(f)
            logger.info(f"Cargadas {len(self.seeds)} variedades desde {seeds_path}")
        except Exception as e:
            logger.error(f"Error cargando seeds.json: {e}")

    def send_message(self, chat_id, text):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            return res.json()
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            return None

    def send_photo(self, chat_id, photo_path, caption):
        url = f"{self.base_url}/sendPhoto"
        
        # Resolver si es ruta relativa
        abs_photo = photo_path
        if not os.path.isabs(photo_path):
            abs_photo = os.path.join(self.repo_dir, photo_path)

        if os.path.exists(abs_photo):
            try:
                with open(abs_photo, 'rb') as photo:
                    files = {'photo': photo}
                    payload = {
                        'chat_id': chat_id,
                        'caption': caption,
                        'parse_mode': 'Markdown'
                    }
                    res = requests.post(url, data=payload, files=files, timeout=20)
                    return res.json()
            except Exception as e:
                logger.error(f"Error subiendo foto local: {e}")

        # Si no existe local o falló, enviar como URL o texto
        if photo_path.startswith("http://") or photo_path.startswith("https://"):
            try:
                payload = {
                    "chat_id": chat_id,
                    "photo": photo_path,
                    "caption": caption,
                    "parse_mode": "Markdown"
                }
                res = requests.post(url, json=payload, timeout=20)
                return res.json()
            except Exception as e:
                logger.error(f"Error enviando foto por URL: {e}")

        # Fallback a mensaje de texto
        return self.send_message(chat_id, caption)

    def format_caption(self, seed: dict) -> str:
        family_clean = seed.get('family', '').lower()
        name_clean = seed.get('name', '').lower()
        
        show_family = bool(family_clean) and (family_clean not in name_clean)
        family_display = f" ({seed['family']})" if show_family else ""
        
        caption = (
            f"🌿 *{seed['name']}*{family_display}\n"
            f"🕒 *Cosecha:* ~{seed.get('harvest_days', '?')} días\n"
            f"📦 *Stock:* {seed.get('stock', 0)} unidades\n"
            f"⚠️ *Desplante:* {seed.get('removal_type', 'N/A')}\n"
            f"📝 _'{seed.get('observations', '')}'_"
        )
        return caption

    def handle_text_query(self, chat_id, query_text):
        norm_query = normalize(query_text)
        if not norm_query:
            return

        if norm_query in ["/start", "start", "/help", "help", "hola"]:
            self.send_message(
                chat_id,
                "🌿 *¡Hola!*\n\nEscribe el nombre de cualquier planta (por ejemplo: `pepino`, `tomate`, `espinaca`, `albahaca`) para consultar su ficha técnica, fotos, tiempos de cosecha y consejos de cultivo."
            )
            return

        # Buscar coincidencias
        exact_matches = []
        partial_matches = []

        for s in self.seeds:
            s_name_norm = normalize(s.get('name', ''))
            if norm_query == s_name_norm:
                exact_matches.append(s)
            elif norm_query in s_name_norm or s_name_norm in norm_query:
                partial_matches.append(s)

        results = exact_matches if exact_matches else partial_matches

        if not results:
            self.send_message(
                chat_id,
                f"🌱 No encontré ninguna variedad que coincida con *\"{query_text}\"* en tu inventario.\n\nPrueba buscando por palabras clave como: `tomate`, `lechuga`, `pepino`, `morron`, etc."
            )
            return

        # Si hay más de 5 coincidencias, mostrar listado para que sea más específico
        if len(results) > 5 and not exact_matches:
            names_text = "\n".join([f"• `{s['name']}`" for s in results])
            self.send_message(
                chat_id,
                f"🌱 Encontré *{len(results)}* variedades relacionadas con *\"{query_text}\"*:\n\n{names_text}\n\nEscribe el nombre específico de la que quieras ver."
            )
            return

        # Enviar cada ficha encontrada
        for s in results:
            caption = self.format_caption(s)
            img_source = s.get('image_path') or s.get('image_url')
            if img_source:
                self.send_photo(chat_id, img_source, caption)
            else:
                self.send_message(chat_id, caption)
            time.sleep(1)

    def poll(self):
        logger.info("Bot HuertAlerta iniciado y escuchando mensajes...")
        while True:
            try:
                # Recargar seeds periódicamente si el archivo cambia
                self.load_seeds()

                url = f"{self.base_url}/getUpdates"
                params = {
                    "offset": self.last_update_id + 1,
                    "timeout": 25,
                    "allowed_updates": ["message"]
                }
                res = requests.get(url, params=params, timeout=30)
                data = res.json()

                if not data.get("ok"):
                    logger.warning(f"Telegram API getUpdates error: {data}")
                    time.sleep(3)
                    continue

                for update in data.get("result", []):
                    self.last_update_id = update["update_id"]
                    msg = update.get("message")
                    if not msg:
                        continue

                    chat_id = str(msg["chat"]["id"])
                    text = msg.get("text", "").strip()

                    # Si hay chats autorizados definidos, filtrar solo a esos
                    if self.authorized_chat_ids and chat_id not in self.authorized_chat_ids:
                        logger.info(f"Ignorando mensaje de chat no autorizado: {chat_id}")
                        continue

                    if text:
                        logger.info(f"Consulta recibida de {chat_id}: '{text}'")
                        self.handle_text_query(chat_id, text)

            except requests.exceptions.RequestException as e:
                logger.error(f"Error de red en polling: {e}")
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error inesperado en polling: {e}", exc_info=True)
                time.sleep(5)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "8938142775:AAGIxh9PKRXIkbC_WeQ6JQ4LIE7a88jUEYY")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "252059583")
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    bot = HuertAlertaBot(token=token, authorized_chat_ids=[chat_id], repo_dir=repo_dir)
    bot.poll()
