from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import typing as t

from app.db import models, schemas

# Get a single document by ID
def get_document(db: Session, document_id: int) -> schemas.Document:
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return schemas.Document.from_orm(document)

# Get a list of documents with optional pagination
def get_documents(db: Session, skip=0, limit=100) -> t.List[schemas.DocumentOut]:
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return [schemas.DocumentOut.from_orm(doc) for doc in documents]

# Create a new document
def create_document(db: Session, document: schemas.DocumentCreate) -> schemas.Document:
    db_document = models.Document(
        title=document.title,
        description=document.description,
        document_type=document.document_type,
        file_weight=document.file_weight,
        pages=document.pages,
        s3_url=document.s3_url,
        user_id=document.user_id,
        uploaded_at=document.uploaded_at,
        updated_at=document.updated_at,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

# Edit an existing document
def edit_document(
    db: Session, document_id: int, document: schemas.DocumentEdit
) -> schemas.Document:
    db_document = get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    update_data = document.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_document, key, value)

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

# Delete a document
def delete_document(db: Session, document_id: int) -> schemas.Document:
    document = get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()
    return document