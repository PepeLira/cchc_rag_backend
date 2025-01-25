from .main_schema import DocumentBase, Tag
from typing import List

class DocumentOut(DocumentBase):
    pass
    id : int = None
    tags : List[Tag]

    class Config:
        orm_mode = True

class DocumentCreate(DocumentBase):
    pass
    user_email : str
    doc_hash : str

    class Config:
        orm_mode = True

class DocumentEdit(DocumentBase):
    pass

    class Config:
        orm_mode = True