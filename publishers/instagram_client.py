import os
import logging
import requests

logger = logging.getLogger("InstagramClient")


class InstagramClient:
    def __init__(self, page_id: str, page_access_token: str):
        self.page_id = page_id
        self.access_token = page_access_token
        self.api_version = "v25.0"
        self.ig_user_id = None
        self._resolve_ig_account()

    def _resolve_ig_account(self):
        try:
            url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}?fields=instagram_business_account&access_token={self.access_token}"
            r = requests.get(url)
            data = r.json()
            ig = data.get("instagram_business_account")
            if ig and ig.get("id"):
                self.ig_user_id = ig["id"]
                logger.info(f"Instagram Business encontrado: {self.ig_user_id}")
            else:
                logger.warning("No hay Instagram Business conectado a esta pagina")
        except Exception as e:
            logger.error(f"Error obteniendo Instagram ID: {e}")

    def is_enabled(self) -> bool:
        return self.ig_user_id is not None

    def post_text(self, message: str) -> bool:
        if not self.ig_user_id:
            return False
        try:
            caption = message[:2200]
            url = f"https://graph.facebook.com/{self.api_version}/{self.ig_user_id}/media"
            params = {
                "image_url": "https://via.placeholder.com/1",  # dummy image
                "caption": caption,
                "access_token": self.access_token,
            }
            r = requests.post(url, params=params)
            data = r.json()
            if "id" not in data:
                logger.error(f"Error creando media en Instagram: {r.text}")
                return False
            creation_id = data["id"]
            pub_url = f"https://graph.facebook.com/{self.api_version}/{self.ig_user_id}/media_publish"
            r2 = requests.post(pub_url, params={"creation_id": creation_id, "access_token": self.access_token})
            if r2.status_code == 200:
                logger.info("Texto publicado en Instagram (con imagen placeholder)")
                return True
            logger.error(f"Error publicando en Instagram: {r2.text}")
            return False
        except Exception as e:
            logger.error(f"Error publicando texto en Instagram: {e}")
            return False

    def post_photo(self, image_path: str, caption: str = "") -> bool:
        if not self.ig_user_id:
            return False
        try:
            imgur_url = self._upload_to_imgur(image_path)
            if not imgur_url:
                return self.post_text(caption)  # fallback a texto

            caption = caption[:2200]
            url = f"https://graph.facebook.com/{self.api_version}/{self.ig_user_id}/media"
            params = {
                "image_url": imgur_url,
                "caption": caption,
                "access_token": self.access_token,
            }
            r = requests.post(url, params=params)
            data = r.json()
            if "id" not in data:
                logger.error(f"Error creando media en Instagram: {r.text}")
                return False

            creation_id = data["id"]
            pub_url = f"https://graph.facebook.com/{self.api_version}/{self.ig_user_id}/media_publish"
            r2 = requests.post(pub_url, params={"creation_id": creation_id, "access_token": self.access_token})
            if r2.status_code == 200:
                logger.info(f"Foto publicada en Instagram")
                return True
            logger.error(f"Error publicando foto en Instagram: {r2.text}")
            return False
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {image_path}")
            return False
        except Exception as e:
            logger.error(f"Error publicando foto en Instagram: {e}")
            return False

    def _upload_to_imgur(self, image_path: str) -> str:
        try:
            with open(image_path, "rb") as f:
                r = requests.post(
                    "https://api.imgur.com/3/image",
                    headers={"Authorization": "Client-ID 2c7e0b6a5a3e4f5"},
                    files={"image": f},
                    timeout=30,
                )
                data = r.json()
                if data.get("success"):
                    url = data["data"]["link"]
                    logger.info(f"Imagen subida a Imgur: {url}")
                    return url
                logger.error(f"Error subiendo a Imgur: {data}")
                return ""
        except Exception as e:
            logger.error(f"Error subiendo a Imgur: {e}")
            return ""
