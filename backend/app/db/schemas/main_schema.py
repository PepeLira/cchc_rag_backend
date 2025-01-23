from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_superuser: bool = False
    first_name: str = None
    last_name: str = None
    role: str = "user"

class DocumentBase(BaseModel):
    doc_hash: str
    title: str
    description: Optional[str] = None
    document_type: Optional[str] = None
    file_weight: Optional[int] = None
    pages: Optional[int] = None
    s3_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str = None
    permissions: str = "user"

class DocumentTags(BaseModel):
    document_id: int
    tag_ids : List[int]

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
    tags: List[Tag] 

    class Config:
        orm_mode = True