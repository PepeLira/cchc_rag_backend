from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_superuser: bool = False
    first_name: str = None
    last_name: str = None
    role: str = "user"
    documents: List[int] = []

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: Optional[str] = None
    file_weight: Optional[int] = None
    pages: Optional[int] = None
    s3_url: Optional[str] = None
    user_id: int 
    user: Optional[int]
    tags: List[int] = []
    uploaded_at: Optional[str] = None
    updated_at: Optional[str] = None

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    documents: List[int] = []

class DocumentTagsBase(BaseModel):
    document_id: int 
    tag_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str = None
    permissions: str = "user"

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True

class Document(DocumentBase):
    id: int

    class Config:
        orm_mode = True

class DocumentTags(DocumentTagsBase):
    id: int

    class Config:
        orm_mode = True