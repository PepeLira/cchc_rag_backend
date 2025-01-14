import logging
import uuid
from pathlib import Path
import re

from .docling_integration import DoclingIntegration
from .openai_client import OpenAIVisionClient
from .chunking import DocumentChunker
from .observer import IObserver
from .document_models import DocumentObject

_log = logging.getLogger(__name__)

class DocumentParser:
    def __init__(
        self,
        openai_api_key: str,
        docling_integration: DoclingIntegration,
        observers: list[IObserver] = None,
        chunk_threshold: float = 0.5,
        chunk_size: int = 512,
        min_sentences: int = 1,
        chunk_flag: bool = False,
        describe_flag: bool = False
    ):
        self.observers = observers if observers is not None else []
        self.docling_integration = docling_integration
        self.openai_api_key = openai_api_key
        self.chunk_flag = chunk_flag
        self.describe_flag = describe_flag

        # Build our chunker client
        self.chunker = DocumentChunker(
            api_key=self.openai_api_key,
            threshold=chunk_threshold,
            chunk_size=chunk_size,
            min_sentences=min_sentences
        )

        # Build our Vision client
        self.vision_client = OpenAIVisionClient(api_key=self.openai_api_key)

    def _notify_observers(self, event_name: str, event_data: dict):
        for obs in self.observers:
            obs.notify(event_name, event_data)

    def _load_document_paths(self, directory):
        return list(Path(directory).glob("*.pdf"))

    def parse_documents(self, documents_folder, base_output_dir: Path):
        document_objects = []

        document_paths = self._load_document_paths(documents_folder)

        for doc_path in document_paths:
            doc_id = str(uuid.uuid4())  # or any other unique ID
            title = doc_path.stem
            doc_output_dir = base_output_dir / f"{title}_{doc_id}"

            # Initialize DocumentObject
            doc_obj = DocumentObject(
                doc_id=doc_id,
                title=title,
                doc_path=doc_path,
                output_dir=doc_output_dir
            )

            # 1. Parse PDF -> HTML (with references to images)
            conversion_result, html_path = self.docling_integration.parse_pdf(
                doc_path, 
                doc_output_dir
            )
            doc_obj.html_path = html_path
            doc_obj.page_number = len(conversion_result.pages)

            self._notify_observers("PDF_PARSED", {"doc_id": doc_id, "html_path": str(html_path)})

            # 2. Look for image references in the HTML
            image_refs = self._extract_image_references(html_path, doc_output_dir)
            doc_obj.image_references = image_refs

            self._notify_observers("IMAGE_REFERENCES_FOUND", {"doc_id": doc_id, "count": len(image_refs)})

            if self.describe_flag:
                # 3. Use the OpenAI Vision endpoint to describe each image
                described_html_path = doc_output_dir / f"{title}_described_images.html"
                described_html_content = self._describe_images_in_html(html_path, image_refs)
                with open(described_html_path, "w", encoding="utf-8") as f:
                    f.write(described_html_content)
                doc_obj.described_html_path = described_html_path

                self._notify_observers("IMAGES_DESCRIBED", {"doc_id": doc_id, "described_html_path": str(described_html_path)})

            if self.chunk_flag:
                # 4. Chunk the text from the described HTML
                with open(described_html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                # You might want a more sophisticated approach to extract text from HTML.
                # Here, we do a simple removal of tags:
                text_content = self._strip_html_tags(html_content)

                chunks = self.chunker.chunk_and_embed(text_content)
                for chunk in chunks:
                    doc_obj.add_chunk(chunk)
                    # if chunker directly stores embeddings in chunk, this step is optional
                    # otherwise, doc_obj.add_embedding(chunk.embedding)
            
                self._notify_observers("DOCUMENT_CHUNKED", {"doc_id": doc_id, "chunks_count": len(chunks)})

            # Done, store doc_obj
            document_objects.append(doc_obj)
        
        return document_objects

    def _strip_html_tags(self, html_content: str) -> str:
        """
        Very naive HTML to text. 
        Improve with a parser like BeautifulSoup for real use.
        """
        text = re.sub('<[^<]+?>', '', html_content)
        return text

    def _extract_image_references(self, html_path: Path, doc_output_dir: Path):
        """
        Scans the HTML for image references and returns a list of image paths or URLs.
        By default docling saves images in a subfolder like <html_filename>+artifacts.
        We'll assume local references, but you may have absolute or relative URLs.
        """
        if not html_path.exists():
            return []

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # A simple regex to get <img src="...">
        image_paths = re.findall(r'<img\s+[^>]*src="([^"]+)"', content)
        # Convert them to full path references
        resolved_paths = []
        for p in image_paths:
            # If docling is storing them in "html_filename+artifacts", handle that
            # doc_output_dir is already the directory with the HTML and images
            resolved_paths.append((doc_output_dir / p).resolve())
        return resolved_paths

    def _describe_images_in_html(self, html_path: Path, image_refs):
        """
        Loads the HTML file, replaces each <img src="..."> with a figure or alt text
        containing the description from the OpenAI Vision endpoint.
        """
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        for img_path in image_refs:
            if img_path.exists():
                # You need a local or remote path for the OpenAIVisionClient
                # If local, maybe first upload or create a data URL, etc.
                # For simplicity, let's use the local path as 'image_url'
                description = self.vision_client.describe_image(str(img_path))
                # Create a <figure> or alt text replacement
                # Let's do a naive approach: <img src="..." alt="{description}">
                pattern = rf'<img\s+[^>]*src="{re.escape(str(img_path.name))}"'
                replacement = fr'<img src="{img_path.name}" alt="{description}"'
                html_content = re.sub(pattern, replacement, html_content)

        return html_content
