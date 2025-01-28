from typing import Optional, List

from .backend_client import BackendClient
from .controller import DocumentController
from .document_models import Document, Chunk
from .pinecone_client import PineconeClient
import pdb
class DatabaseSyncService:
    """
    Synchronizes local documents with the hosted (remote) database.
    """

    def __init__(self, controller: DocumentController):
        """
        :param controller:    An instance of DocumentController for local DB operations.
        :param backend_client:An instance of BackendClient for remote API calls.
        """
        self.controller = controller
        self.backend_client = BackendClient()
        self.pinecone_client = PineconeClient()

    def push(self, merge: bool = False):
        """
        Push local documents to the remote backend. 
        If the Pinecone client is set, also upsert the chunks into Pinecone.
        """
        newest_docs = self._update_newest_docs(merge=merge)
        
        # If we have a Pinecone client and the newest docs are not None/empty, do the upsert.
        if self.pinecone_client and newest_docs:
            self._upsert_docs_with_chunks(newest_docs)
    
    def _update_newest_docs(self, merge: bool = False):
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
                "pages": doc.page_count,
                "document_type": "pdf",
                "user_email": "admin@cchc-rag.com"
            }

            if doc.local_update == 1:
                # The doc already exists on the backend
                if merge:
                    # Update on the backend
                    print(f"Updating doc_hash='{doc.doc_hash}' on the remote server...")
                    self.backend_client.update_document_by_hash(doc.doc_hash, doc_data)
                    self._mark_as_uploaded(doc)
                    self._no_local_update(doc)
                else:
                    # Skip creating or updating
                    print(f"Skipping doc_hash='{doc.doc_hash}' because merge=False and local_update=1.")
            else:
                # local_update == 0 => doc is brand new on the backend
                print(f"Creating doc_hash='{doc.doc_hash}' on the remote server...")
                self.backend_client.create_document(doc_data)
                self._mark_as_uploaded(doc)
        
        return newest_docs
    
    def _upsert_docs_with_chunks(self, docs: List[Document]):
        """
        Upserts the chunks of the given documents into the Pinecone vector store
        (if the documents actually have chunks with embeddings).
        
        :param docs: List of Document objects whose chunks should be upserted.
        """
        # Filter only docs that actually have chunk embeddings
        documents_with_embeddings = []
        for doc in docs:
            # Keep only chunks with non-empty embeddings
            valid_chunks = [ch for ch in doc.chunks if ch.embedding.any()]
            if valid_chunks:
                # Temporarily store only the valid chunks for each doc
                # You can either store them on the object or build a new structure.
                doc.chunks = valid_chunks
                documents_with_embeddings.append(doc)

        if not documents_with_embeddings:
            print("No chunks with embeddings found among newest_docs.")
            return

        print("Upserting document chunks into Pinecone...")
        self.pinecone_client.upsert_documents(
            documents_with_embeddings, namespace="cchc-chunks"
        )
        print("Upsert complete.")

    def _mark_as_uploaded(self, doc: Document):
        """
        Marks a document as uploaded (is_uploaded=1) in the local DB and commits.
        """
        doc.is_uploaded = 1
        self.controller.db_session.add(doc)
        self.controller.db_session.commit()
        self.controller.db_session.refresh(doc)
        print(f"Document id={doc.id} (hash={doc.doc_hash}) marked as uploaded.")

    def _no_local_update(self, doc: Document) -> bool:
        """
        Marks a document as not needing an update on the backend.
        """
        doc.local_update = 0
        self.controller.db_session.add(doc)
        self.controller.db_session.commit()
        self.controller.db_session.refresh(doc)
        print(f"Document id={doc.id} (hash={doc.doc_hash}) marked as no local update.")
