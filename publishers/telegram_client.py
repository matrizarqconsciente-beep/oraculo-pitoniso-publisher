import os
import logging
import requests

logger = logging.getLogger("TelegramClient")


class TelegramClient:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        if not self.bot_token or not self.channel_id:
            logger.warning("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID en .env")
            self.enabled = False
            return
        self.enabled = True
        self.base = f"https://api.telegram.org/bot{self.bot_token}"
        logger.info("TelegramClient inicializado")

    def _call(self, method, **kwargs):
        url = f"{self.base}/{method}"
        try:
            r = requests.post(url, **kwargs, timeout=15)
            data = r.json()
            if data.get("ok"):
                return True
            logger.error(f"Error Telegram: {data}")
            return False
        except Exception as e:
            logger.error(f"Error Telegram: {e}")
            return False

    def post_text(self, message: str) -> bool:
        if not self.enabled:
            return False
        return self._call("sendMessage", json={
            "chat_id": self.channel_id,
            "text": message[:4096],
            "parse_mode": "HTML"
        })

    def post_photo(self, image_path: str, caption: str = "") -> bool:
        if not self.enabled:
            return False
        try:
            with open(image_path, "rb") as f:
                files = {"photo": f}
                data = {"chat_id": self.channel_id, "caption": caption[:1024]}
                return self._call("sendPhoto", data=data, files=files)
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {image_path}")
            return False
