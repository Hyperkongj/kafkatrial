import logging
from mastodon import StreamListener

class CustomListener(StreamListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Map the event "status.update" (with a dot) to our on_status_update method.
        setattr(self, "on_status.update", self.on_status_update)

    def on_status_update(self, status):
        logging.info("Received updated status: %s", status)
        # TODO: Process the status update (e.g., forward to Kafka, perform sentiment analysis, etc.)

    def on_unknown_event(self, event):
        # If the unknown event is actually a status.update, handle it as one.
        if event.get("event") == "status.update":
            self.on_status_update(event.get("data"))
        else:
            logging.warning("Unknown event received: %s", event)
