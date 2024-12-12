from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.schemas.document_schema import Document
    from app.db.schemas.tag_schema import Tag

class DocumentTagsBase(BaseModel):
    document_id: int 
    tag_id: int
    tag: 'Tag'
    document: 'Document'

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