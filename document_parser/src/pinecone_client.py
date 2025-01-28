from typing import List
import itertools

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

from .chunking import DocumentChunker

from .document_models import Document, Chunk
from .config import PINECONE_API_KEY, OPENAI_API_KEY
import pdb

class PineconeClient:
    def __init__(
        self,
        index_name: str = "cchc-index",
        dimension: int = 1536,
        region: str = "us-east-1",
        metric: str = "cosine",
        deletion_protection: str = "disabled",
        batch_size: int = 200,  # <--- default batch size for upserts
    ):
        """
        Initializes the Pinecone client and sets up (or creates) a Pinecone index.
        """
        self.api_key = PINECONE_API_KEY
        self.index_name = index_name
        self.dimension = dimension
        self.region = region
        self.metric = metric
        self.deletion_protection = deletion_protection
        self.batch_size = batch_size

        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)

        # Check if index exists, otherwise create it
        existing_indexes = [idx["name"] for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(cloud="aws", region=self.region),
                deletion_protection=self.deletion_protection,
            )

        # Prepare the index handle for upserts/queries
        self.index = self.pc.Index(self.index_name)

    def _chunked(self, iterable, batch_size):
        """
        A helper generator function to break an iterable into chunks
        of size `batch_size`.
        """
        it = iter(iterable)
        chunk = tuple(itertools.islice(it, batch_size))
        while chunk:
            yield chunk
            chunk = tuple(itertools.islice(it, batch_size))

    def upsert_documents(
        self, documents: List[Document], namespace: str = "cchc-chunks"
    ):
        """
        Upsert the chunks of given documents into Pinecone in batches.

        :param documents: List of Document objects (with associated chunks).
        :param namespace: Pinecone namespace to upsert vectors into.
        """
        # Accumulate all vectors to upsert
        vectors_to_upsert = []
        for doc in documents:
            for chunk in doc.chunks:
                if chunk.embedding is None:
                    continue
                vector_record = {
                    "id": f"doc_{doc.id}_chunk_{chunk.id}",
                    "values": chunk.embedding,  # the embedding array
                    "metadata": {
                        "document_id": doc.id,
                        "document_title": doc.title,
                        "text": chunk.text,
                        "markdown_path": doc.markdown_path,
                    },
                }
                vectors_to_upsert.append(vector_record)

        if not vectors_to_upsert:
            print("No valid embeddings found to upsert.")
            return

        total_vectors = len(vectors_to_upsert)
        print(
            f"Upserting {total_vectors} vectors in batches of size {self.batch_size}..."
        )

        # Upsert in batches
        for i, chunked_batch in enumerate(
            self._chunked(vectors_to_upsert, self.batch_size), start=1
        ):
            self.index.upsert(vectors=chunked_batch, namespace=namespace)
            print(
                f"  Batch {i} with {len(chunked_batch)} vectors upserted successfully."
            )

        print(
            f"Done! Upserted a total of {total_vectors} vectors into namespace '{namespace}'."
        )

    def query_text(
        self, query_text: str, top_k: int = 3, namespace: str = "cchc-chunks"
    ):
        """
        Query Pinecone for the top_k most similar vectors to the provided query text.

        :param query_text: The text to be embedded and queried.
        :param top_k:      How many results to return.
        :param namespace:  The namespace to query within.
        :param chunker:    Optional. If the PineconeClient was not constructed with a chunker,
                                           you must provide one here; otherwise, we use `self.chunker`.
        """

        active_chunker = DocumentChunker(api_key=OPENAI_API_KEY)

        # Embed the text into a vector
        query_vector = active_chunker.embed(query_text)

        # Query Pinecone
        response = self.index.query(
            namespace=namespace,
            vector=query_vector,
            top_k=top_k,
            include_values=True,
            include_metadata=True,
        )

        # pdb.set_trace()
        text_responses = [match.metadata for match in response.matches]
        return text_responses

    def purge_namespace(self, namespace: str = "cchc-chunks"):
        """
        Delete all vectors in the given namespace.
        """
        self.index.delete(delete_all=True, namespace=namespace)
        print(f"Purged all vectors in namespace '{namespace}'.")
