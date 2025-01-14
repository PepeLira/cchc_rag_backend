import logging
from abc import ABC, abstractmethod

_log = logging.getLogger(__name__)

class IObserver(ABC):

    @abstractmethod
    def notify(self, event_name: str, event_data: dict):
        pass


class LoggingObserver(IObserver):

    def __init__(self, log_file_path):
        self.log_file_path = log_file_path

    def notify(self, event_name: str, event_data: dict):
        message = f"Event: {event_name}, Data: {event_data}"
        _log.info(message)
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")
