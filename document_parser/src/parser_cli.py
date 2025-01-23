import logging
from pathlib import Path
from IPython import embed  # IPython interactive shell

from .database import SessionLocal, init_db
from .controller import DocumentController

from .document_models import Document, Chunk, Tag

def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    session = SessionLocal()
    controller = DocumentController(session)

    local_ns = {
        'session': session,
        'controller': controller,
        'Document': Document,
        'Chunk': Chunk,
        'Tag': Tag
    }

    print("Launching IPython console. Available objects:")
    print(" - session: SQLAlchemy session")
    print(" - controller: DocumentController instance")
    print(" To query models, use `session.query(Model).all()`")
    print("Type `exit` or press Ctrl-D to exit.")

    # Launch IPython shell with local namespace
    embed(user_ns=local_ns)

if __name__ == "__main__":
    main()