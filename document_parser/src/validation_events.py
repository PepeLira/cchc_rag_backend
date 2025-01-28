from sqlalchemy import event
from sqlalchemy.orm import Session
from .document_models import Document
from .backend_client import BackendClient
from .observer import IObserver

class ValidationEvents:
    def __init__(self, observers: list[IObserver] = None):
        self.observers = observers if observers else []

        event.listen(Document, "before_insert", self.check_doc_hash_in_backend)

    def check_doc_hash_in_backend(self, mapper, connection, target):
        """
        This will be called before an INSERT on the Document table.
        'target' is the Document instance being persisted.
        """
        if target.doc_hash:
            client = BackendClient()
            result = client.check_document_hash(target.doc_hash)

            if result.get("exists"):
                target.local_update = 1
                self._notify_observers(
                    "ValidationEvent",
                    {
                        "message": f"Document '{target.title}' already on backend. Marked local_update=1."
                    },
                )

    def _notify_observers(self, event_name, event_data):
        for obs in self.observers:
            obs.notify(event_name, event_data)