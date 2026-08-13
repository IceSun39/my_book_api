from typing import List
import src.backend.services.author_service as author_service
from src.backend.schemas.author_schemas import AuthorResponse, AuthorCreate
from src.backend.schemas.book_schemas import BookResponse
from src.backend.database.database import get_session
from src.backend.core.dependencies import get_current_user, get_current_admin_user
from src.backend.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

author_router = APIRouter(
    prefix="/api/authors",
    tags=["authors"],
)


@author_router.get("/", response_model=List[AuthorResponse])
async def get_authors(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    return await author_service.get_all_authors(session)


@author_router.get("/{author_id}/books", response_model=List[BookResponse], status_code=200)
async def get_all_books(author_id: int, session: AsyncSession = Depends(get_session),
                        current_user: User = Depends(get_current_user)):
    return await author_service.get_all_author_books(session, author_id)


@author_router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int, session: AsyncSession = Depends(get_session),
                     current_user: User = Depends(get_current_user)):
    return await author_service.get_author(session, author_id)


@author_router.post("/", response_model=AuthorResponse, status_code=201)
async def add_author(author: AuthorCreate, session: AsyncSession = Depends(get_session),
                     admin_user: User = Depends(get_current_admin_user)):
    return await author_service.add_author(session, author)


@author_router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(author_id: int, author_update: AuthorCreate, session: AsyncSession = Depends(get_session),
                        admin_user: User = Depends(get_current_admin_user)):
    return await author_service.update_author(session, author_id, author_update)


@author_router.delete("/{author_id}", status_code=204)
async def delete_author(author_id: int, session: AsyncSession = Depends(get_session),
                        admin_user: User = Depends(get_current_admin_user)):
    deleted_author = await author_service.delete_author(session, author_id)
