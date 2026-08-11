from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException

from src.backend.models.book import Book
from src.backend.models.author import Author
from src.backend.schemas.book_schemas import BookCreate, BookResponse


def add_book(session: Session, book_create: BookCreate) -> BookResponse:
    authors = session.query(Author).filter(Author.author_id.in_(book_create.author_ids)).all()

    if not authors:
        raise HTTPException(status_code=404, detail="Author not found")

    book = Book(
        book_title=book_create.book_title,
        publish_date=book_create.publish_date,
        created_at=datetime.now(timezone.utc),
        authors=authors
    )

    session.add(book)
    session.commit()
    session.refresh(book)

    book_response = BookResponse.model_validate(book)
    return book_response


def update_book(session: Session, book_id: int, book_update: BookCreate) -> Optional[BookResponse]:
    stmt = session.query(Book).where(Book.book_id == book_id)
    existing_book = session.scalars(stmt).one_or_none()

    if existing_book is None:
        return None
    for key, value in book_update.model_dump().items():
        setattr(existing_book, key, value)
    session.commit()
    session.refresh(existing_book)
    return existing_book

def delete_book(session: Session, book_id: int) -> Optional[BookResponse]:
    stmt = session.query(Book).where(Book.book_id == book_id)
    existing_book = session.scalars(stmt).one_or_none()

    if existing_book is None:
        return None

    session.delete(existing_book)
    session.commit()
    session.refresh(existing_book)
    return existing_book

def get_book(session: Session, book_id: int) -> Optional[BookResponse]:
    stmt = session.query(Book).where(Book.book_id == book_id)
    existing_book = session.scalars(stmt).one_or_none()
    if existing_book is None:
        return None
    return existing_book

def get_books(session: Session) -> List[BookResponse]:
    stmt = session.query(Book)
    books = session.scalars(stmt).all()
    return [BookResponse.model_validate(book) for book in books]