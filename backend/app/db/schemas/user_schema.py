from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from app.db.schemas.document_schema import Document
class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_superuser: bool = False
    first_name: str = None
    last_name: str = None
    role: str = "user"
    documents: List['Document'] = []

    class Config:
        arbitrary_types_allowed = True

class UserOut(UserBase):
    pass

class UserCreate(UserBase):
    password: str

    class Config:
        orm_mode = True

class UserEdit(UserBase):
    password: Optional[str] = None

    class Config:
        orm_mode = True

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
