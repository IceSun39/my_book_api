from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated
from datetime import datetime

class BookCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=50)]
    author: Annotated[str, Field(min_length=1, max_length=50)]
    publish_date: Annotated[datetime, Field()]


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    publish_date: datetime