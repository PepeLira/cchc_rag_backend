import logging
import argparse
import sys
from pathlib import Path

from IPython import embed  # IPython interactive shell

from .database import SessionLocal, init_db
from .controller import DocumentController
from .document_models import Document, Chunk, Tag

from .observer import LoggingObserver
from .validation_events import ValidationEvents
from .docling_integration import DoclingIntegration
from .document_parser import DocumentParser
from .database_sync_service import DatabaseSyncService

from .config import (
    OPENAI_API_KEY,
    TEST_PARSE_FOLDER
)


def resolve_documents_folder(folder_str: str | None) -> Path:
    """
    Resolves the documents folder from a string path.
    If None is provided, falls back to TEST_PARSE_FOLDER.
    Checks if the folder exists; otherwise raises FileNotFoundError.
    """
    if folder_str is None:
        folder_str = TEST_PARSE_FOLDER

    folder = Path(folder_str)
    if not folder.is_dir():
        raise FileNotFoundError(f"Documents folder not found: {folder.resolve()}")
    return folder


def run(documents_folder: str = None, base_output_dir: str = None) -> None:
    """
    Launches an IPython CLI that provides:
        - A session with SQLAlchemy
        - A DocumentController instance
        - A configured DocumentParser instance
        - A set of instructions for parsing documents
        - A set of instructions for changing the documents folder interactively
        - A DatabaseSyncService instance for syncing local documents with the backend

    :param documents_folder: Path to the folder containing documents to parse.
    :param base_output_dir:  Path to the output folder for parsed documents and logs.
    :raises FileNotFoundError: If the documents_folder does not exist.
    """
    logging.basicConfig(level=logging.INFO)

    # --- Initialize the Database and Session ---
    init_db()
    session = SessionLocal()
    controller = DocumentController(session)

    # --- Determine/Validate the Documents Folder ---
    doc_folder = resolve_documents_folder(documents_folder)

    # --- Determine the Base Output Directory ---
    if base_output_dir is None:
        base_output_dir = "parsed_docs"
    base_output_dir = Path(base_output_dir)
    base_output_dir.mkdir(parents=True, exist_ok=True)

    # --- Set up Observers and Parser ---
    docling_integration = DoclingIntegration()
    log_file_path = base_output_dir / "processing.log"
    observer = LoggingObserver(log_file_path=str(log_file_path))
    data_validator = ValidationEvents(observers=[observer])

    parser = DocumentParser(
        openai_api_key=OPENAI_API_KEY,
        docling_integration=docling_integration,
        observers=[observer],
        chunk_threshold=0.5,
        chunk_size=512,
        min_sentences=1,
        controller=controller
    )

    # --- Provide a helper function to change folder interactively ---
    def set_documents_folder(new_folder: str):
        """
        Updates the documents_folder used by parser and local namespace.
        Checks existence and raises FileNotFoundError if invalid.
        """
        path_obj = Path(new_folder)
        if not path_obj.is_dir():
            raise FileNotFoundError(f"Documents folder not found: {path_obj.resolve()}")
        local_ns["documents_folder"] = path_obj
        print(f"documents_folder changed to: {path_obj.resolve()}")

    def parse_documents(
        chunk: bool = False, describe: bool = False, reprocess: bool = False
    ):
        """
        Parses the documents in the current documents_folder.
        """
        return parser.parse_documents(
            doc_folder, base_output_dir, chunk, describe, reprocess
        )

    # --- Prepare Local Namespace for IPython ---
    local_ns = {
        "session": session,
        "controller": controller,
        "Document": Document,
        "Chunk": Chunk,
        "Tag": Tag,
        "parse_documents": parse_documents,
        "documents_folder": doc_folder,   # Initially set
        "base_output_dir": base_output_dir,
        "set_documents_folder": set_documents_folder,  # Our new function
        "backend_sync": DatabaseSyncService(controller),
    }

    # --- Print Usage Instructions ---
    print("\nLaunching IPython console. Available objects:")
    print(" - session:             SQLAlchemy session")
    print(" - controller:          DocumentController instance")
    print(" - Document, Chunk, Tag: ORM models")
    print(" - parse_documents:     Parse documents from 'documents_folder' to 'base_output_dir'")
    print(" - documents_folder:    Current path to documents to parse")
    print(" - base_output_dir:     Output path for logs & parsed docs")
    print(" - set_documents_folder(new_folder): changes 'documents_folder' after checks\n")
    print(" - backend_sync:        DatabaseSyncService(controller) instance for syncing\n")
    print("Commands you can use inside IPython:")
    print("  1) session.query(Document).all()")
    print("  2) parser.parse_documents(documents_folder, base_output_dir)")
    print("  3) set_documents_folder('/path/to/new/folder')")
    print("  4) exit / Ctrl-D to exit the shell\n")

    # --- Start IPython Session ---
    embed(user_ns=local_ns)


if __name__ == "__main__":
    parser_cli = argparse.ArgumentParser(description="Parser CLI")
    parser_cli.add_argument(
        "--documents_folder",
        type=str,
        help="Path to the documents folder"
    )
    parser_cli.add_argument(
        "--output_dir",
        type=str,
        help="Base output directory for parsed docs and logs"
    )
    args = parser_cli.parse_args()

    try:
        run(
            documents_folder=args.documents_folder,
            base_output_dir=args.output_dir
        )
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)
