from .main_schema import DocumentBase

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