import logging
from pathlib import Path

from .docling_integration import DoclingIntegration
from .document_parser import DocumentParser
from .observer import LoggingObserver
from .config import OPENAI_API_KEY, TEST_PARSE_FOLDER

def main():
    logging.basicConfig(level=logging.INFO)

    openai_api_key = OPENAI_API_KEY

    documents_folder = Path("path/to/documents")
    if not documents_folder.exists():
        documents_folder = Path(TEST_PARSE_FOLDER)
    if not documents_folder.exists():
        raise Exception(f"Documents folder not found: {documents_folder}")
    
    base_output_dir = Path("parsed_docs")
    docling_integration = DoclingIntegration()

    observer = LoggingObserver(log_file_path=str(base_output_dir / "processing.log"))

    # Create the DocumentParser
    parser = DocumentParser(
        openai_api_key=openai_api_key,
        docling_integration=docling_integration,
        observers=[observer],
        chunk_threshold=0.5,
        chunk_size=512,
        min_sentences=1
    )

    # Parse documents
    result_docs = parser.parse_documents(documents_folder, base_output_dir)

    for doc_obj in result_docs:
        print(f"Parsed Document: {doc_obj.doc_id}")
        print(f" - Title: {doc_obj.title}")
        print(f" - HTML Path: {doc_obj.html_path}")
        print(f" - Described HTML Path: {doc_obj.described_html_path}")
        print(f" - # of Chunks: {len(doc_obj.chunks)}")

if __name__ == "__main__":
    main()
