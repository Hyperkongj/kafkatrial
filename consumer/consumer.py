import os
import json
import logging
from time import sleep
from kafka import KafkaConsumer
from processor import process_message

logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, kafka_server: str, kafka_topic: str):
        self.server = kafka_server
        self.topic = kafka_topic
        self.consumer = None
        self.connect()

    def connect(self):
        """Connect to Kafka and create a consumer."""
        while True:
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=[self.server],
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id="mastodon_consumer_group",
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                )
                logger.info("Connected to Kafka: %s, topic=%s", self.server, self.topic)
                break
            except Exception as e:
                logger.exception("Error connecting to Kafka: %s", e)
                sleep(5)

    def poll_messages(self):
        """Yield messages from the Kafka topic indefinitely."""
        for msg in self.consumer:
            yield msg.value

    def close(self):
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed.")
