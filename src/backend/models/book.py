from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.backend.database import Base
from src.backend.models.associations import user_favorite_books
from src.backend.models.associations.books_and_authors import books_and_authors
from src.backend.models.author import Author

if TYPE_CHECKING:
    from src.backend.models.user import User

class Book(Base):
    __tablename__ = "book"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    book_title: Mapped[str] = mapped_column(String(50))
    publish_date: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    authors: Mapped[List[Author]] = relationship(
        secondary=books_and_authors,
        back_populates="books"
    )

    favorited_by: Mapped[List[User]] = relationship(
        secondary=user_favorite_books,
        back_populates="favorite_books"
    )