from pydantic import BaseModel
from app.db.models.user import User
from app.db.models.tag import Tag
import typing as t

class DocumentBase(BaseModel):
    title: str
    description: t.Optional[str] = None
    document_type: t.Optional[str] = None
    file_weight: t.Optional[int] = None
    pages: t.Optional[int] = None
    s3_url: t.Optional[str] = None
    user_id: int 
    user: User
    tags: t.List[Tag] = []
    uploaded_at: t.Optional[str] = None
    updated_at: t.Optional[str] = None

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