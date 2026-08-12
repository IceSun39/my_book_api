from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from fastapi import HTTPException

from src.backend.models.book import Book
from src.backend.models.author import Author
from src.backend.models.user import User
from src.backend.schemas.book_schemas import BookCreate, BookResponse

async def add_book(session: AsyncSession, book_create: BookCreate) -> BookResponse:
    stmt = select(Author).where(Author.author_id.in_(book_create.author_ids))

    result = await session.execute(stmt)
    authors = list(result.scalars().all())

    if not authors:
        raise HTTPException(status_code=404, detail="Author not found")

    book = Book(
        book_title=book_create.book_title,
        publish_date=book_create.publish_date,
        created_at=datetime.now(timezone.utc),
        authors=authors
    )

    session.add(book)
    await session.commit()
    await session.refresh(book)

    book_response = BookResponse.model_validate(book)
    return book_response


async def update_book(session: AsyncSession, book_id: int, book_update: BookCreate) -> Optional[BookResponse]:
    stmt = select(Book).where(Book.book_id == book_id).options(selectinload(Book.authors))
    result = await session.execute(stmt)
    existing_book = result.scalars().one_or_none()

    if existing_book is None:
        return None


    update_data = book_update.model_dump(exclude={"author_ids"})
    for key, value in update_data.items():
        setattr(existing_book, key, value)

    if book_update.author_ids:
        author_stmt = select(Author).where(Author.author_id.in_(book_update.author_ids)).options(selectinload(Book.authors))
        author_result = await session.execute(author_stmt)
        new_authors = list(author_result.scalars().all())

        if not new_authors:
            raise HTTPException(status_code=404, detail="Authors not found")

        existing_book.authors = new_authors

    await session.commit()
    await session.refresh(existing_book)

    return BookResponse.model_validate(existing_book)


async def delete_book(session: AsyncSession, book_id: int) -> Optional[BookResponse]:
    stmt = select(Book).where(Book.book_id == book_id).options(selectinload(Book.authors))
    result = await session.execute(stmt)
    existing_book = result.scalars().one_or_none()

    if existing_book is None:
        return None

    await session.delete(existing_book)
    await session.commit()

    return BookResponse.model_validate(existing_book)


async def get_book(session: AsyncSession, book_id: int) -> Optional[BookResponse]:
    stmt = select(Book).where(Book.book_id == book_id).options(selectinload(Book.authors))
    result = await session.execute(stmt)
    existing_book = result.scalars().one_or_none()

    if existing_book is None:
        return None

    return BookResponse.model_validate(existing_book)


async def get_all_books(session: AsyncSession) -> List[BookResponse]:
    stmt = select(Book).options(selectinload(Book.authors))
    result = await session.execute(stmt)
    books = result.scalars().all()

    return [BookResponse.model_validate(book) for book in books]


async def get_favorite_books(session: AsyncSession, user_id: int) -> List[Book]:
    stmt = select(User).where(User.user_id == user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return []

    sorted_books = sorted(user.favorite_books, key=lambda book: book.book_id, reverse=True)

    return sorted_books