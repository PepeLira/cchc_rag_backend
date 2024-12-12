from pydantic import BaseModel
from app.db.models import Document
import typing as t

class TagBase(BaseModel):
    name: str
    description: t.Optional[str] = None
    is_active: bool = True
    documents: t.List[Document] = []

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