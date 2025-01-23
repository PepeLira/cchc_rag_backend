import logging
import uuid
from pathlib import Path
import re

from .docling_integration import DoclingIntegration
from .openai_client import OpenAIVisionClient
from .chunking import DocumentChunker
from .observer import IObserver
from .controller import DocumentController

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
        describe_flag: bool = False,
        controller: DocumentController = None
    ):
        self.observers = observers if observers is not None else []
        self.docling_integration = docling_integration
        self.openai_api_key = openai_api_key
        self.chunk_flag = chunk_flag
        self.describe_flag = describe_flag
        self.controller = controller

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
            doc_path_id = str(uuid.uuid4())  # or any other unique ID
            title = doc_path.stem
            doc_output_dir = base_output_dir / f"{title}_{doc_path_id}"

            # Initialize DocumentObject
            doc_obj = self.controller.create_document(
                title=title,
                doc_path=str(doc_path),
                output_dir=str(doc_output_dir),
                doc_hash=None
            )

            # [!] Parse PDF -> markdown (with references to images)
            conversion_result, markdown_path = self.docling_integration.parse_pdf(
                doc_path, 
                doc_output_dir
            )

            doc_obj.markdown_path = str(markdown_path)
            markdown_file_name = markdown_path.stem
            doc_obj.images_path = str(doc_output_dir / f"{markdown_file_name}_artifacts")
            doc_obj.page_count = len(conversion_result.pages)
            doc_obj.doc_hash = conversion_result.document.origin.binary_hash # This is the hash of the binary content of the document

            self._notify_observers("PDF_PARSED", {"doc_path_id": doc_path_id, "markdown_path": str(markdown_path)})

            if self.describe_flag:
                # TODO: "Implement image description"
                # [!] Use the OpenAI Vision endpoint to describe each image
                # described_markdown_path = doc_output_dir / f"{title}_described_images.markdown"
                # described_markdown_content = self._describe_images_in_markdown(markdown_path)
                # with open(described_markdown_path, "w", encoding="utf-8") as f:
                #     f.write(described_markdown_content)
                # doc_obj.described_markdown_path = described_markdown_path
                pass

                self._notify_observers("IMAGES_DESCRIBED", {"doc_path_id": doc_path_id, "described_markdown_path": str("Here is the path")})

            if self.chunk_flag:
                # [!] Chunk the text from the described markdown
                with open(markdown_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                # You might want a more sophisticated approach to extract text from markdown.
                # Here, we do a simple removal of tags:
                text_content = self._strip_markdown_tags(markdown_content)

                chunks = self.chunker.chunk_and_embed(text_content)
                chunks_objects = []

                for chunk in chunks:
                    chunk_o = self.controller.create_chunk(
                        document_id=doc_obj.id,
                        text = chunk.text,
                        embedding = chunk.embedding
                    )
                    chunks_objects.append(chunk_o)
                doc_obj.chunks = chunks_objects

                self._notify_observers("DOCUMENT_CHUNKED", {"doc_path_id": doc_path_id, "chunks_count": len(chunks)})
            
            self.controller.commit(doc_obj) # Done, store doc_obj in the database
            document_objects.append(doc_obj)
        
        return document_objects

    def _strip_markdown_tags(self, markdown_content: str) -> str:
        """
        Very naive markdown to text. 
        Improve with a parser like BeautifulSoup for real use.
        """
        text = re.sub('<[^<]+?>', '', markdown_content)
        return text

    def _extract_image_references(self, markdown_path: Path, doc_output_dir: Path):
        """
        Scans the markdown for image references and returns a list of image paths or URLs.
        By default docling saves images in a subfolder like <markdown_filename>+artifacts.
        We'll assume local references, but you may have absolute or relative URLs.
        """
        if not markdown_path.exists():
            return []

        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # A simple regex to get <img src="...">
        image_paths = re.findall(r'<img\s+[^>]*src="([^"]+)"', content)
        # Convert them to full path references
        resolved_paths = []
        for p in image_paths:
            # If docling is storing them in "markdown_filename+artifacts", handle that
            # doc_output_dir is already the directory with the markdown and images
            resolved_paths.append((doc_output_dir / p).resolve())
        return resolved_paths

    def _describe_images_in_markdown(self, markdown_path: Path, image_refs):
        """
        Loads the markdown file, replaces each <img src="..."> with a figure or alt text
        containing the description from the OpenAI Vision endpoint.
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

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
                markdown_content = re.sub(pattern, replacement, markdown_content)

        return markdown_content
