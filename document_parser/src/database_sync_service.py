from typing import Optional

from .backend_client import BackendClient
from .controller import DocumentController
from .document_models import Document

class DatabaseSyncService:
    """
    Synchronizes local documents with the hosted (remote) database.
    """

    def __init__(self, controller: DocumentController, backend_client: BackendClient):
        """
        :param controller:    An instance of DocumentController for local DB operations.
        :param backend_client:An instance of BackendClient for remote API calls.
        """
        self.controller = controller
        self.backend_client = backend_client

    def push(self, merge: bool = False):
        """
        Pushes local documents (is_uploaded = 0) to the remote backend.
        
        - If a document has local_update = 1, that means it's already on the backend.
          If `merge == True`, we update it on the backend. If `merge == False`, we skip it.
        - If a document has local_update = 0, we create a new document on the backend.
        - After a successful create or update, set is_uploaded = 1 to mark it as synced.
        """
        # 1) Fetch local docs that are not uploaded yet
        newest_docs = self.controller.get_newest_documents()
        if not newest_docs:
            print("No new documents to push.")
            return

        for doc in newest_docs:
            # 2) Build the data payload for the remote API
            doc_data = {
                "doc_hash": doc.doc_hash,
                "title": doc.title,
                "doc_path": doc.doc_path,
                "output_dir": doc.output_dir,
                "markdown_path": doc.markdown_path,
                "images_path": doc.images_path,
                "page_count": doc.page_count,
                # Add other fields as needed by the backend
            }

            if doc.local_update == 1:
                # The doc already exists on the backend
                if merge:
                    # Update on the backend
                    print(f"Updating doc_hash='{doc.doc_hash}' on the remote server...")
                    self.backend_client.update_document_by_hash(doc.doc_hash, doc_data)
                    self._mark_as_uploaded(doc)
                else:
                    # Skip creating or updating
                    print(f"Skipping doc_hash='{doc.doc_hash}' because merge=False and local_update=1.")
            else:
                # local_update == 0 => doc is brand new on the backend
                print(f"Creating doc_hash='{doc.doc_hash}' on the remote server...")
                self.backend_client.create_document(doc_data)
                self._mark_as_uploaded(doc)

    def _mark_as_uploaded(self, doc: Document):
        """
        Marks a document as uploaded (is_uploaded=1) in the local DB and commits.
        """
        doc.is_uploaded = 1
        self.controller.db_session.add(doc)
        self.controller.db_session.commit()
        self.controller.db_session.refresh(doc)
        print(f"Document id={doc.id} (hash={doc.doc_hash}) marked as uploaded.")
