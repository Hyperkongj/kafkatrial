import os
import logging
from time import sleep
from dotenv import load_dotenv
from mastodon import Mastodon, StreamListener
from producer import Producer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
MASTODON_API_BASE_URL = os.getenv("MASTODON_API_BASE_URL")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "mastodon_updates")

if not (MASTODON_ACCESS_TOKEN and MASTODON_API_BASE_URL):
    logger.error("Missing Mastodon credentials (MASTODON_ACCESS_TOKEN, MASTODON_API_BASE_URL).")
    exit(1)

# Initialize Mastodon client
mastodon_client = Mastodon(
    access_token=MASTODON_ACCESS_TOKEN,
    api_base_url=MASTODON_API_BASE_URL
)

# Initialize Kafka producer
producer = Producer(kafka_server=KAFKA_SERVER, kafka_topic=KAFKA_TOPIC)

class MastodonListener(StreamListener):
    def on_update(self, status):
        try:
            if isinstance(status, dict):
                username = status.get("account", {}).get("username", "unknown")
                content = status.get("content", "")
                created_at = status.get("created_at", "")
                logger.info("New toot from @%s at %s", username, created_at)
                producer.send({
                    "username": username,
                    "content": content,
                    "created_at": created_at
                })
            else:
                logger.warning("Received update in unexpected format: %s", status)
        except Exception as e:
            logger.exception("Error processing Mastodon update: %s", e)

    def on_error(self, error):
        logger.error("Mastodon stream error: %s", error)
        # Return True to keep stream alive after an error
        return True

def main():
    listener = MastodonListener()
    while True:
        try:
            logger.info("Starting Mastodon public stream...")
            mastodon_client.stream_public(listener)
        except Exception as e:
            logger.exception("Stream failed: %s", e)
            sleep(10)

if __name__ == "__main__":
    main()
