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
from src.backend.services.user_services import get_user

async def get_book(session: AsyncSession, book_id: int) -> Optional[BookResponse]:
    stmt = select(Book).where(Book.book_id == book_id).options(selectinload(Book.authors))
    result = await session.execute(stmt)
    existing_book = result.scalars().one_or_none()

    if existing_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return BookResponse.model_validate(existing_book)

async def add_book(session: AsyncSession, book_create: BookCreate) -> BookResponse:
    stmt = select(Author).where(Author.author_id.in_(book_create.author_ids))

    result = await session.execute(stmt)
    authors = list(result.scalars().all())

    if not authors:
        raise HTTPException(status_code=404, detail="Author not found")

    publish_date_naive = book_create.publish_date.replace(
        tzinfo=None) if book_create.publish_date.tzinfo else book_create.publish_date

    created_at_naive = datetime.now(timezone.utc).replace(tzinfo=None)

    book = Book(
        book_title=book_create.book_title,
        publish_date=publish_date_naive,
        created_at=created_at_naive,
        authors=authors
    )

    session.add(book)
    await session.commit()
    await session.refresh(book)

    stmt_refresh = select(Book).where(Book.book_id == book.book_id).options(selectinload(Book.authors))
    result_refresh = await session.execute(stmt_refresh)
    complete_book = result_refresh.scalar_one()

    book_response = BookResponse.model_validate(complete_book)
    return book_response


async def update_book(session: AsyncSession, book_id: int, book_update: BookCreate,) -> Optional[BookResponse]:
    existing_book = await get_book(session, book_id)

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

    if "publish_date" in update_data and update_data["publish_date"].tzinfo:
        update_data["publish_date"] = update_data["publish_date"].replace(tzinfo=None)

    await session.commit()
    await session.refresh(existing_book)

    return BookResponse.model_validate(existing_book)


async def delete_book(session: AsyncSession, book_id: int) -> BookResponse:
    existing_book = await get_book(session, book_id)

    await session.delete(existing_book)
    await session.commit()

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

async def add_favorite(session: AsyncSession, book_id: int, user_id: int) -> dict:
    favorite_book = await get_book(session, book_id)

    user = await get_user(session, user_id)

    if any(b.book_id == book_id for b in user.favorite_books):
        return {"message": "Book already favorited"}

    user.favorite_books.append(favorite_book)
    await session.commit()
    return {'message': f'{favorite_book.book_title} added to {user_id} favorite_books'}

async def remove_favorite(session: AsyncSession, book_id: int, user_id: int) -> dict:
    user = await get_user(session, user_id)

    book_to_remove = next((b for b in user.favorite_books if b.book_id == book_id), None)

    if not book_to_remove:
        return {"message": "Book is not favorited"}

    user.favorite_books.remove(book_to_remove)

    await session.commit()
    return {'message': f'{book_to_remove.book_title} removed from favorites'}