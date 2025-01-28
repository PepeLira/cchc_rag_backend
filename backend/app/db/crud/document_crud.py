from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import typing as t

from .tag_crud import get_tags_by_name_list
from app.db import models, schemas

def get_document(db: Session, document_id: int) -> models.Document:
    """Return the ORM instance of a document."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

def get_document_by_hash(db: Session, doc_hash: str) -> models.Document:
    """Return the ORM instance of a document."""
    document = db.query(models.Document).filter(models.Document.doc_hash == doc_hash).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

def get_documents(db: Session, skip=0, limit=100) -> t.List[schemas.DocumentOut]:
    """Returns a list of documents as schemas for read-only purposes."""
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return [schemas.DocumentOut.from_orm(doc) for doc in documents]

def create_document(db: Session, document: schemas.DocumentCreate) -> models.Document:
    """Create a new document and return the ORM instance."""
    user_id = db.query(models.User).filter(models.User.email == document.user_email).first().id
    db_document = models.Document(
        doc_hash=document.doc_hash,
        title=document.title,
        description=document.description,
        document_type=document.document_type,
        file_weight=document.file_weight,
        pages=document.pages,
        s3_url=document.s3_url,
        user_id=user_id,
        uploaded_at=document.uploaded_at,
        updated_at=document.updated_at,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def edit_document(db: Session, document_id: int, document: schemas.DocumentEdit) -> models.Document:
    """Edit an existing document and return the updated ORM instance."""
    db_document = get_document(db, document_id)  # ORM instance
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    update_data = document.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_document, key, value)

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int) -> models.Document:
    """Delete a document and return the deleted ORM instance."""
    document = get_document(db, document_id)  # ORM instance
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()
    return document

def add_tags_to_document(db: Session, document_id: int, tags_names: t.List[str]) -> models.Document:
    """Add multiple tags to a document and return the updated ORM instance."""
    document = get_document(db, document_id)  # ORM instance
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    tags = get_tags_by_name_list(db, tags_names)  # Should return ORM instances of Tag
    if not tags:
        raise HTTPException(status_code=404, detail="No tags found for the given IDs")

    for tag in tags:
        if tag not in document.tags:
            document.tags.append(tag)

    db.commit()
    db.refresh(document)
    return document

def remove_document_tag(db: Session, document_id: int, tags_names: t.List[str]) -> models.Document:
    """Remove multiple tags from a document and return the updated ORM instance."""
    document = get_document(db, document_id)  # ORM instance
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    tags = get_tags_by_name_list(db, tags_names)  # ORM instances of Tag
    if not tags:
        raise HTTPException(status_code=404, detail="No tags found for the given IDs")

    for tag in tags:
        if tag in document.tags:
            document.tags.remove(tag)
        else:
            raise HTTPException(status_code=404, detail=f"Tag Name:{tag.name} not found")

    db.commit()
    db.refresh(document)
    return document
