from .main_schema import TagBase

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