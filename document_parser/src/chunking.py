import logging
from chonkie import SemanticChunker
from chonkie import OpenAIEmbeddings

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

        self._embedder = OpenAIEmbeddings(
            api_key=self.openai_api_key,
            model=self.embedding_model
        )
        self.embedding_size = self._embedder._dimension

    def chunk_and_embed(self, text: str):
        chunks = self._chunker.chunk(text)
        _log.info(f"Document chunked into {len(chunks)} segments.")
        for chunk in chunks:
            chunk.embedding = self._embedder.embed(chunk.text)
        _log.info("Document chunks embedded.")
        return chunks
    
    def embed(self, text: str):
        embedded_text = self._embedder.embed(text)
        _log.info("Text embedded.")
        return embedded_text