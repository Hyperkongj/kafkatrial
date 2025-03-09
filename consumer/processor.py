import logging

logger = logging.getLogger(__name__)

def process_message(message: dict) -> dict:
    """
    Process or transform the incoming Kafka message as needed.
    For now, we just log and return it unmodified.
    """
    username = message.get("username", "unknown")
    logger.info("Processing message from user: %s", username)
    # Add any transformations, NLP, or extra fields if needed
    return message
