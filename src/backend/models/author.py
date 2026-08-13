from __future__ import annotations
from typing import List, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.backend.database import Base
from src.backend.models.associations.books_and_authors import books_and_authors

if TYPE_CHECKING:
    from src.backend.models.book import Book

class Author(Base):
    __tablename__ = "author"
    author_id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    books: Mapped[List[Book]] = relationship(
        secondary="books_and_authors",
        back_populates="authors"
    )
