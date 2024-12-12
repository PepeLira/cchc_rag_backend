from .main_schema import UserBase
from typing import Optional

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
