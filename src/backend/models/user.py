from __future__ import annotations
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.backend.database import Base
from src.backend.models.associations import user_favorite_books

if TYPE_CHECKING:
    from src.backend.models.book import Book

class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column()

    favorite_books: Mapped[List[Book]] = relationship(
        secondary="user_favorite_books",
        back_populates="favorited_by"
    )