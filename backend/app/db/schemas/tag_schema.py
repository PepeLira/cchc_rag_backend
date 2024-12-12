from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from app.db.schemas.document_schema import Document

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    documents: List['Document'] = []

    class Config:
        arbitrary_types_allowed = True

class TagOut(TagBase):
    pass

class TagCreate(TagBase):
    pass

    class Config:
        orm_mode = True

class TagEdit(TagBase):
    pass

    class Config:
        orm_mode = True

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True