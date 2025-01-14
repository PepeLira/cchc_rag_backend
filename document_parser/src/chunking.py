import logging
from chonkie import SemanticChunker

_log = logging.getLogger(__name__)

class DocumentChunker:

    def __init__(self, api_key: str, embedding_model: str = "text-embedding-3-small",
                 threshold: float = 0.5, chunk_size: int = 512, min_sentences: int = 1):
        self.openai_api_key = api_key
        self.embedding_model = embedding_model
        self.threshold = threshold
        self.chunk_size = chunk_size
        self.min_sentences = min_sentences

        self._chunker = SemanticChunker(
            embedding_model=self.embedding_model,
            threshold=self.threshold,
            chunk_size=self.chunk_size,
            min_sentences=self.min_sentences,
            api_key=self.openai_api_key
        )

    def chunk_and_embed(self, text: str):
        chunks = self._chunker.chunk(text)
        _log.info(f"Document chunked into {len(chunks)} segments.")
        return chunks
