from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List, Optional


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    book_title: str


class AuthorCreate(BaseModel):
    fullname: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[str, Field(min_length=1, max_length=100)]
    book_ids: List[int] = Field(default_factory=list)


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: int
    fullname: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[str, Field(min_length=1, max_length=100)]
    books: List[BookResponse] = Field(default_factory=list)
