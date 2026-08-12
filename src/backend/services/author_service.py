from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from src.backend.models.book import Book
from src.backend.models.author import Author
from src.backend.schemas.author_schemas import AuthorResponse, AuthorCreate


async def add_author(session: AsyncSession, author_create: AuthorCreate) -> AuthorResponse:
    author = Author(
        **author_create.model_dump(exclude={"book_ids"})
    )

    if author_create.book_ids:
        stmt = select(Book).where(Book.book_id.in_(author_create.book_ids))
        result = await session.execute(stmt)
        books = list(result.scalars().all())

        if not books:
            raise HTTPException(status_code=404, detail="Books not found")

        author.books = books

    session.add(author)
    await session.commit()
    await session.refresh(author)
    return AuthorResponse.model_validate(author)


async def update_author(session: AsyncSession, author_id: int, author_update: AuthorCreate) -> AuthorResponse:
    stmt = select(Author).where(Author.author_id == author_id).options(selectinload(Author.books))
    result = await session.execute(stmt)
    existing_book = result.scalar_one_or_none()

    if existing_book is None:
        raise HTTPException(status_code=404, detail="Author not found")

    update_data = author_update.model_dump(exclude={"book_ids"})
    for key, value in update_data.items():
        setattr(existing_book, key, value)

    if author_update.book_ids:
        book_stmt = select(Book).where(Book.book_id.in_(author_update.book_ids))
        result = await session.execute(book_stmt)
        new_books = list(result.scalars().all())

        if not new_books:
            raise HTTPException(status_code=404, detail="Books not found")

        existing_book.books = new_books

    await session.commit()
    await session.refresh(existing_book)

    return AuthorResponse.model_validate(existing_book)


async def delete_author(session: AsyncSession, author_id: int) -> Optional[AuthorResponse]:
    stmt = select(Author).where(Author.author_id == author_id).options(selectinload(Author.books))
    result = await session.execute(stmt)
    existing_author = result.scalar_one_or_none()

    if existing_author is None:
        return None

    await session.delete(existing_author)
    await session.commit()

    return AuthorResponse.model_validate(existing_author)


async def get_author(session: AsyncSession, author_id: int) -> Optional[AuthorResponse]:
    stmt = select(Author).where(Author.author_id == author_id).options(selectinload(Author.books))
    result = await session.execute(stmt)
    existing_author = result.scalar_one_or_none()

    if existing_author is None:
        return None

    return AuthorResponse.model_validate(existing_author)


async def get_all_authors(session: AsyncSession) -> List[AuthorResponse]:
    stmt = select(Author).options(selectinload(Author.books))
    result = await session.execute(stmt)
    existing_authors = result.scalars().all()

    return [AuthorResponse.model_validate(author) for author in existing_authors]
