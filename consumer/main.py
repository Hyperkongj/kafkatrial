import os
import logging
from time import sleep
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from processor import process_message


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from .env (optional if you prefer config files)
load_dotenv()

# Read environment variables
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "mastodon_updates")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "mastodon_index")

def main():
    # Connect to Elasticsearch
    es_client = None
    while True:
        try:
            es_client = Elasticsearch(ELASTICSEARCH_HOST)
            if es_client.ping():
                logger.info("Connected to Elasticsearch at %s", ELASTICSEARCH_HOST)
                break
            else:
                logger.error("Elasticsearch ping failed. Retrying...")
        except Exception as e:
            logger.exception("Error connecting to Elasticsearch: %s", e)
        sleep(5)

    # Ensure index exists
    if not es_client.indices.exists(index=ELASTICSEARCH_INDEX):
        es_client.indices.create(index=ELASTICSEARCH_INDEX)
        logger.info("Created index: %s", ELASTICSEARCH_INDEX)

    # Start Kafka consumer
    consumer = consumer(KAFKA_SERVER, KAFKA_TOPIC)

    try:
        for raw_msg in consumer.poll_messages():
            processed = process_message(raw_msg)
            # Index into Elasticsearch
            try:
                resp = es_client.index(index=ELASTICSEARCH_INDEX, body=processed)
                logger.info("Indexed doc: result=%s", resp.get("result"))
            except Exception as index_err:
                logger.exception("Error indexing doc to ES: %s", index_err)
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")

    consumer.close()

if __name__ == "__main__":
    main()
