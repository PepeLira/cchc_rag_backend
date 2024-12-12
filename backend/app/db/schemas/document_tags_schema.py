from pydantic import BaseModel
import typing as t
from app.db.models import Document
from app.db.models import Tag

class DocumentTagsBase(BaseModel):
    document_id: int 
    tag_id: int
    tag: Tag
    document: Document

    class Config:
        arbitrary_types_allowed = True

class DocumentTagsOut(DocumentTagsBase):
    pass

class DocumentTagsCreate(DocumentTagsBase):
    pass

    class Config:
        orm_mode = True

class DocumentTags(DocumentTagsBase):
    id: int

    class Config:
        orm_mode = True