import json
import logging
from time import sleep
from kafka import KafkaProducer

logger = logging.getLogger(__name__)

class Producer:
    def __init__(self, kafka_server: str, kafka_topic: str):
        self.server = kafka_server
        self.topic = kafka_topic
        self.producer = None
        self.connect()

    def connect(self):
        while True:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=[self.server],
                    value_serializer=lambda v: json.dumps(v, default=lambda o: o.isoformat() if hasattr(o, 'isoformat') else o).encode("utf-8")

                )
                logger.info("Connected to Kafka at %s", self.server)
                break
            except Exception as e:
                logger.exception("Error connecting to Kafka: %s", e)
                sleep(5)

    def send(self, data: dict):
        try:
            future = self.producer.send(self.topic, data)
            future.get(timeout=10)
            logger.info("Sent message to topic=%s", self.topic)
        except Exception as e:
            logger.exception("Error sending message to Kafka: %s", e)
