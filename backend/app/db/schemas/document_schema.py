from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from app.db.schemas.user_schema import User
    from app.db.schemas.tag_schema import Tag

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: Optional[str] = None
    file_weight: Optional[int] = None
    pages: Optional[int] = None
    s3_url: Optional[str] = None
    user_id: int 
    user: Optional['User']
    tags: List['Tag'] = []
    uploaded_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class DocumentOut(DocumentBase):
    pass

class DocumentCreate(DocumentBase):
    pass

    class Config:
        orm_mode = True

class DocumentEdit(DocumentBase):
    pass

    class Config:
        orm_mode = True

class Document(DocumentBase):
    id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True