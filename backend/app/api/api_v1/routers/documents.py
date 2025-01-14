from fastapi import APIRouter, Request, Depends
from fastapi import Body, Response, encoders
import typing as t
from app.db.session import get_db
from app.db.crud.document_crud import (
    get_documents,
    get_document,
    create_document,
    delete_document,
    edit_document,
    add_tags_to_document,
    remove_document_tag,
)
from app.db.schemas import DocumentCreate, DocumentEdit, Document, DocumentOut
from app.core.auth import get_current_active_user, get_current_active_superuser


documents_router = r = APIRouter()

@r.get(
    "/documents",
    response_model=t.List[Document],
    response_model_exclude_none=True,
)
async def documents_list(
    response: Response,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """
    Get all documents
    """
    documents = get_documents(db)
    # This is necessary for react-admin to work
    response.headers["Content-Range"] = f"0-9/{len(documents)}"
    return documents

@r.get(
    "/document/{document_id}",
    response_model=Document,
    response_model_exclude_none=True,
)
async def document_details(
    request: Request,
    document_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Get a specific document by ID
    """
    document = get_document(db, document_id)
    return document

@r.post(
    "/documents", 
    response_model=Document, 
    response_model_exclude_none=True
)
async def document_create(
    request: Request,
    document: DocumentCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Create a new document
    """
    return create_document(db, document)

@r.put(
    "/document/{document_id}",
    response_model=Document,
    response_model_exclude_none=True,
)
async def document_edit(
    request: Request,
    document_id: int,
    document: DocumentEdit,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Edit a document by ID
    """
    return edit_document(db, document_id, document)

@r.delete(
    "/document/{document_id}",
    response_model=Document,
    response_model_exclude_none=True,
)
async def document_delete(
    request: Request,
    document_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Delete a document by ID
    """
    return delete_document(db, document_id)

@r.post(
    "/documents/{document_id}/add_tags",
    response_model=Document,
    response_model_exclude_none=True,
)
async def document_add_tag(
    request: Request,
    document_id: int,
    tags_names: t.List[str] = Body(
        ...,
        description="A list of tag Names to associate with the specified document.",
        example=["int_tag_id_1", "int_tag_id_2", "int_tag_id_3"]
    ),
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Add a tag to a document
    """
    return add_tags_to_document(db, document_id, tags_names) 

@r.post(
    "/documents/{document_id}/remove_tags",
    response_model=Document,
    response_model_exclude_none=True,
)
async def document_remove_tag(
    request: Request,
    document_id: int,
    tags_names: t.List[str] = Body(
        ...,
        description="A list of tag Names to associate with the specified document.",
        example=["int_tag_id_1", "int_tag_id_2", "int_tag_id_3"]
    ),
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Remove a tag from a document
    """
    return remove_document_tag(db, document_id, tags_names)