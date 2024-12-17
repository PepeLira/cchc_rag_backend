from fastapi import APIRouter, Request, Depends, Response, encoders
import typing as t

from app.db.session import get_db
from app.db.crud.tag_crud import (
    get_tags,
    get_tag,
    create_tag,
    delete_tag,
    edit_tag,
)
from app.db.schemas import TagCreate, TagEdit, Tag, TagOut
from app.core.auth import get_current_active_user, get_current_active_superuser

tags_router = r = APIRouter()

@r.get(
    "/tags",
    response_model=t.List[Tag],
    response_model_exclude_none=True,
)
async def tags_list(
    response: Response,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """
    Get all tags
    """
    tags = get_tags(db)
    # This is necessary for react-admin to work
    response.headers["Content-Range"] = f"0-9/{len(tags)}"
    return tags

@r.get(
    "/tag/{tag_id}",
    response_model=Tag,
    response_model_exclude_none=True,
)
async def tag_details(
    request: Request,
    tag_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Get a specific tag by ID
    """
    tag = get_tag(db, tag_id)
    return tag

@r.post(
    "/tags", 
    response_model=Tag, 
    response_model_exclude_none=True
)
async def tag_create(
    request: Request,
    tag: TagCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """
    Create a new tag
    """
    return create_tag(db, tag)

@r.put(
    "/tag/{tag_id}", 
    response_model=Tag, 
    response_model_exclude_none=True
)
async def tag_edit(
    request: Request,
    tag_id: int,
    tag: TagEdit,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """
    Edit an existing tag
    """
    return edit_tag(db, tag_id, tag)

@r.delete(
    "/tag/{tag_id}", 
    response_model=Tag, 
    response_model_exclude_none=True
)
async def tag_delete(
    request: Request,
    tag_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """
    Delete a tag by ID
    """
    return delete_tag(db, tag_id)