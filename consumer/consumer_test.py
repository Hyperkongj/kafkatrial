#!/usr/bin/env python3
"""
consumer_test.py

This script subscribes to the Kafka topic "mastodon_updates" and prints out
the messages received.

Because kafka‑python (v2.0.2) expects to import vendor modules that aren’t
present in your environment (e.g., kafka.vendor.six.moves and kafka.vendor.socketpair),
we perform a monkey‑patch before any kafka‑python imports.
"""

import sys
import types
import socket
import six

# --- Monkey-Patch Start ---
# Create (or get) the "kafka.vendor" module.
if "kafka.vendor" not in sys.modules:
    vendor_module = types.ModuleType("kafka.vendor")
    sys.modules["kafka.vendor"] = vendor_module
else:
    vendor_module = sys.modules["kafka.vendor"]

# Inject six and its moves into the vendor namespace.
vendor_module.six = six
sys.modules["kafka.vendor.six"] = six
sys.modules["kafka.vendor.six.moves"] = six.moves

# For socketpair: use the built‑in socket.socketpair if available.
if not hasattr(vendor_module, "socketpair"):
    try:
        vendor_module.socketpair = socket.socketpair
    except AttributeError:
        # On some systems (e.g. Windows) socketpair is not available.
        def dummy_socketpair():
            raise NotImplementedError("socketpair is not supported on this platform.")
        vendor_module.socketpair = dummy_socketpair
# --- Monkey-Patch End ---

import logging
from kafka import KafkaConsumer

# Configure logging.
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Create a Kafka consumer subscribed to the "mastodon_updates" topic.
consumer = KafkaConsumer(
    "mastodon_updates",
    bootstrap_servers=["kafka:9092"],
    auto_offset_reset="earliest",
    group_id="consumer-group"
)

logger.info("Consumer connected. Listening for messages...")

try:
    for message in consumer:
        try:
            msg_str = message.value.decode("utf-8")
            logger.info("Received message: %s", msg_str)
        except Exception as e:
            logger.exception("Error processing message: %s", e)
except KeyboardInterrupt:
    logger.info("Consumer interrupted. Exiting...")
