import os
import requests
import logging

logger = logging.getLogger("FacebookClient")


class FacebookClient:
    def __init__(self, page_id: str, page_access_token: str):
        self.page_id = page_id
        self.access_token = page_access_token
        self.api_version = "v25.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}"

    def post_text(self, message: str) -> bool:
        url = f"{self.base_url}/feed"
        params = {"message": message, "access_token": self.access_token}
        try:
            resp = requests.post(url, params=params)
            if resp.status_code == 200:
                post_id = resp.json().get("id", "?")
                logger.info(f"Post publicado en Facebook (post_id: {post_id})")
                return True
            logger.error(f"Error Facebook: {resp.status_code} - {resp.text}")
            return False
        except Exception as e:
            logger.error(f"Error publicando en Facebook: {e}")
            return False

    def post_photo(self, image_path: str, message: str = "") -> bool:
        url = f"{self.base_url}/photos"
        try:
            with open(image_path, "rb") as img:
                files = {"source": img}
                data = {"message": message, "access_token": self.access_token}
                resp = requests.post(url, files=files, data=data)
                if resp.status_code == 200:
                    post_id = resp.json().get("id", "?")
                    logger.info(f"Foto publicada en Facebook (post_id: {post_id})")
                    return True
                logger.error(f"Error Facebook foto: {resp.status_code} - {resp.text}")
                return False
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {image_path}")
            return False
        except Exception as e:
            logger.error(f"Error publicando foto: {e}")
            return False
