from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List
from datetime import datetime

class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: int
    fullname: str

class BookCreate(BaseModel):
    book_title: Annotated[str, Field(min_length=1, max_length=50)]
    author_ids: Annotated[List[int], Field(min_length=1)]
    publish_date: Annotated[datetime, Field()]

class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    book_title: str
    publish_date: datetime
    created_at: datetime

    authors: List[AuthorResponse]