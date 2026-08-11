from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List, Optional

class FavoriteBookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    book_title: str

class UserBase(BaseModel):
    email: Annotated[str, Field(min_length=1, max_length=50)]
    first_name: Annotated[Optional[str], Field(min_length=1, max_length=50)] = None
    last_name: Annotated[Optional[str], Field(min_length=1, max_length=50)] = None

class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8)]

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    is_admin: bool
    favorite_books: List[FavoriteBookResponse] = []

class UserUpdate(BaseModel):
    email: Annotated[Optional[str], Field(min_length=1, max_length=50)] = None
    first_name: Annotated[Optional[str], Field(min_length=1, max_length=50)] = None
    last_name: Annotated[Optional[str], Field(min_length=1, max_length=50)] = None
    password: Annotated[Optional[str], Field(min_length=8)] = None

class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    is_admin: bool
    hashed_password: str