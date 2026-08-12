import src.backend.services.book_services as book_services
from src.backend.schemas.book_schemas import BookCreate, BookResponse
from src.backend.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

book_router = APIRouter(
    prefix="/api/books",
    tags=["books"],
)

@book_router.get("/", response_model=BookResponse)
async def get_books(session: AsyncSession = Depends(get_session)):
    return await book_services.get_all_books(session)

@book_router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book = await book_services.get_book(session, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@book_router.post("/", response_model=BookResponse, status_code=201)
async def add_book(book: BookCreate, session: AsyncSession = Depends(get_session)):
    return await book_services.add_book(session, book)

@book_router.put("/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate, session: AsyncSession = Depends(get_session)):
    updated_book = await book_services.update_book(session, book_id, book)
    if updated_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@book_router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    deleted_book = await book_services.delete_book(session, book_id)
    if deleted_book is None:
        raise HTTPException(status_code=404, detail="Book not found")