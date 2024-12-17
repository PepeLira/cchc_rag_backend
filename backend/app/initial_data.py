#!/usr/bin/env python3

from app.db.session import SessionLocal
from app.db.session import get_db
from app.db.crud.user_crud import create_user
from app.db.crud.tag_crud import create_tag
from app.db.crud.document_crud import (
    create_document, 
    add_tags_to_document, 
    get_document
)
from app.db.schemas import UserCreate
from app.db.schemas import TagCreate
from app.db.schemas import DocumentCreate



def init() -> None:
    db = SessionLocal()

    create_user(
        db,
        UserCreate(
            email="admin@cchc-rag.com",
            password="9cc4cfac3aff75e4fc69",
            is_active=True,
            is_superuser=True,
        ),
    )

    create_tag(
        db,
        TagCreate(
            name="tag1",
            description="tag1 description",
            is_active=True,
        ),
    )

    create_tag(
        db,
        TagCreate(
            name="tag2",
            description="tag2 description",
            is_active=True,
        ),
    )

    last_document = get_document(db, 1)

    add_tags_to_document(
        db,
        last_document.id,
        [1, 2],
    )

    db.close()


if __name__ == "__main__":
    print("Creating superuser and test data")
    init()
    print("Superuser created")
