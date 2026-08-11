from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List

from models.book import Book

class FavoriteBooks(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    favorite_book_id: int
    favorite_book_title: str

class User(BaseModel):
    email: Annotated[str, Field(min_length=1, max_length=50)]
    first_name: Annotated[str | None, Field(min_length=1, max_length=50)]
    last_name: Annotated[str | None, Field(min_length=1, max_length=50)]
    password: Annotated[str, Field(min_length=8)]
    is_admin: Annotated[bool, Field()]
    favorite_books: Annotated[List[Book], Field()]

class UserCreate(User):
    pass

class UserInDB(User):
    hashed_password: str

class UserResponse(User):
    user_id: int
    first_name: str | None
    last_name: str | None
    is_admin: bool
    favorite_books: List[FavoriteBooks]