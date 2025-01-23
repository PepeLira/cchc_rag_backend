import logging
from pathlib import Path

from src.docling_integration import DoclingIntegration
from src.document_parser import DocumentParser
from src.observer import LoggingObserver
from src.config import OPENAI_API_KEY, TEST_PARSE_FOLDER

from src.database import SessionLocal, init_db
from src.validation_events import ValidationEvents
from src.controller import DocumentController

init_db()

session = SessionLocal()
controller = DocumentController(session)

def main():
    logging.basicConfig(level=logging.INFO)

    documents_folder = Path("path/to/documents")
    if not documents_folder.exists():
        documents_folder = Path(TEST_PARSE_FOLDER)
    if not documents_folder.exists():
        raise Exception(f"Documents folder not found: {documents_folder}")
    
    base_output_dir = Path("parsed_docs")
    docling_integration = DoclingIntegration()

    # Create the Log observer
    observer = LoggingObserver(log_file_path=str(base_output_dir / "processing.log"))
    data_validator = ValidationEvents(observers=[observer])

    # Create the DocumentParser
    parser = DocumentParser(
        openai_api_key=OPENAI_API_KEY,
        docling_integration=docling_integration,
        observers=[observer],
        chunk_threshold=0.5,
        chunk_size=512,
        min_sentences=1,
        controller=controller,
        chunk_flag = False
    )

    # Parse documents
    result_docs = parser.parse_documents(documents_folder, base_output_dir)

    for doc_obj in result_docs:
        print(f"Parsed Document: {doc_obj.doc_hash}")
        print(f" - Title: {doc_obj.title}")
        print(f" - markdown Path: {doc_obj.markdown_path}")
        print(f" - reference images path: {doc_obj.images_path}")
        print(f" - # of Chunks: {len(doc_obj.chunks)}")

if __name__ == "__main__":
    main()
