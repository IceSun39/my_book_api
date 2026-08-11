from sqlalchemy import Table, Column, ForeignKey
from src.backend.database import Base

books_and_authors= Table(
    "books_and_authors",
    Base.metadata,
    Column("author_id", ForeignKey("author.author_id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", ForeignKey("book.book_id", ondelete="CASCADE"), primary_key=True),
)