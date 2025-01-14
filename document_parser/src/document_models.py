from pathlib import Path
from typing import List, Optional

class DocumentObject:
    def __init__(
        self,
        doc_id: str,
        title: str,
        doc_path: Path,
        output_dir: Path,
        page_number: Optional[int] = None
    ):
        self.doc_id = doc_id
        self.title = title
        self.doc_path = doc_path
        self.page_number = page_number

        self.output_dir = output_dir
        self.html_path: Optional[Path] = None
        self.described_html_path: Optional[Path] = None

        self.chunks: List = []
        self.embeddings: List = []  # or integrated with the chunk objects
        self.image_references: List[Path] = []  # references to the image files, if any

    def add_chunk(self, chunk):
        self.chunks.append(chunk)

    def add_embedding(self, embedding):
        self.embeddings.append(embedding)
