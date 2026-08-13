from typing import List
import src.backend.services.book_services as book_services
from src.backend.schemas.book_schemas import BookCreate, BookResponse
from src.backend.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from src.backend.core.dependencies import get_current_user, get_current_admin_user
from src.backend.models.user import User

book_router = APIRouter(
    prefix="/api/books",
    tags=["books"],
)


@book_router.get("/favorite", response_model=List[BookResponse])
async def get_all_favorite(session: AsyncSession = Depends(get_session),
                           current_user: User = Depends(get_current_user)):
    return await book_services.get_favorite_books(session, current_user.user_id)


@book_router.post("/favorite/{book_id}", response_model=dict, status_code=201)
async def add_favorite(book_id: int, session: AsyncSession = Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    return await book_services.add_favorite(session, book_id, current_user.user_id)


@book_router.delete("/favorite/{book_id}", status_code=204)
async def remove_favorite(book_id: int, session: AsyncSession = Depends(get_session),
                          current_user: User = Depends(get_current_admin_user)):
    return await book_services.remove_favorite(session, book_id, current_user.user_id)


@book_router.get("/", response_model=List[BookResponse])
async def get_books(session: AsyncSession = Depends(get_session)):
    return await book_services.get_all_books(session)


@book_router.get("/favorite", response_model=List[BookResponse])
async def get_favorite(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    return await book_services.get_favorite_books(session, current_user.user_id)


@book_router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    return await book_services.get_book(session, book_id)


@book_router.post("/", response_model=BookResponse, status_code=201)
async def add_book(book: BookCreate, session: AsyncSession = Depends(get_session),
                   admin_user: User = Depends(get_current_admin_user)):
    return await book_services.add_book(session, book)


@book_router.put("/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate, session: AsyncSession = Depends(get_session),
                      admin_user: User = Depends(get_current_admin_user)):
    return await book_services.update_book(session, book_id, book)


@book_router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session),
                      admin_user: User = Depends(get_current_admin_user)):
    deleted_book = await book_services.delete_book(session, book_id)
