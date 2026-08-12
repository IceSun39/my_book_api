from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List
from datetime import datetime

class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    book_title: str


class AuthorCreate(BaseModel):
    fullname: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[str, Field(min_length=1, max_length=100)]
    book_ids: Annotated[List[int], Field(min_length=1)]

class AuthorResponse(BaseModel):
    fullname: Annotated[str, Field(min_length=1, max_length=100)]
    books: Annotated[List[BookResponse], Field(min_length=1)]