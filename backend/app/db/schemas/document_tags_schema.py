from .main_schema import DocumentTagsBase

class DocumentTagsOut(DocumentTagsBase):
    pass

class DocumentTagsCreate(DocumentTagsBase):
    pass

    class Config:
        orm_mode = True