import os
import logging
import tweepy

logger = logging.getLogger("TwitterClient")


class TwitterClient:
    def __init__(self):
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        if not all([api_key, api_secret, access_token, access_secret]):
            logger.error("Faltan credenciales de Twitter en .env (TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)")
            self.client = None
            return

        try:
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
            )
            logger.info("TwitterClient inicializado")
        except Exception as e:
            logger.error(f"Error inicializando TwitterClient: {e}")
            self.client = None

    def post_text(self, message: str) -> bool:
        if not self.client:
            return False
        try:
            tweet = message[:280]
            resp = self.client.create_tweet(text=tweet)
            if resp.data and resp.data.get("id"):
                logger.info(f"Tweet publicado (id: {resp.data['id']})")
                return True
            logger.error(f"Error publicando tweet: {resp}")
            return False
        except Exception as e:
            logger.error(f"Error publicando tweet: {e}")
            return False

    def post_photo(self, image_path: str, message: str = "") -> bool:
        if not self.client:
            return False
        try:
            import requests
            from requests_oauthlib import OAuth1

            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_secret = os.getenv("TWITTER_ACCESS_SECRET")

            auth = OAuth1(api_key, api_secret, access_token, access_secret)

            upload_url = "https://upload.twitter.com/1.1/media/upload.json"
            with open(image_path, "rb") as f:
                files = {"media": f}
                r = requests.post(upload_url, auth=auth, files=files)
                if r.status_code != 200:
                    logger.error(f"Error subiendo imagen a Twitter: {r.status_code} - {r.text}")
                    return False
                media_id = r.json()["media_id_string"]

            tweet_text = message[:280] if message else ""
            resp = self.client.create_tweet(text=tweet_text, media_ids=[media_id])
            if resp.data and resp.data.get("id"):
                logger.info(f"Tweet con foto publicado (id: {resp.data['id']})")
                return True
            logger.error(f"Error publicando tweet con foto: {resp}")
            return False
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {image_path}")
            return False
        except Exception as e:
            logger.error(f"Error publicando tweet con foto: {e}")
            return False
