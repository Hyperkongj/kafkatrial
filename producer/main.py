import os
import logging
from time import sleep
from dotenv import load_dotenv
from mastodon import Mastodon
from producer import Producer
from listener import CustomListener  # Import our custom listener

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# Retrieve credentials and configuration from environment variables
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

# Initialize Kafka producer (assumes producer.py implements a Producer class with a send method)
producer = Producer(kafka_server=KAFKA_SERVER, kafka_topic=KAFKA_TOPIC)

def main():
    # Instantiate the custom listener from listener.py
    listener = CustomListener()
    while True:
        try:
            logger.info("Starting Mastodon public stream...")
            mastodon_client.stream_public(listener)
        except Exception as e:
            logger.exception("Stream failed: %s", e)
            sleep(10)

if __name__ == "__main__":
    main()
