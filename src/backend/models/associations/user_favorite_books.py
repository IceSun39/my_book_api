from sqlalchemy import Table, Column, ForeignKey
from src.backend.database import Base

user_favorite_books = Table(
    "user_favorite_books",
    Base.metadata,
    Column("user_id", ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", ForeignKey("book.book_id", ondelete="CASCADE"), primary_key=True),
)