import src.backend.services.author_service as author_service
from src.backend.schemas.author_schemas import AuthorResponse, AuthorCreate
from src.backend.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

author_router = APIRouter(
    prefix="/api/author",
    tags=["author"],
)

@author_router.get("/", response_model=AuthorResponse)
async def get_authors(session: AsyncSession = Depends(get_session)):
    return await author_service.get_all_authors(session)

@author_router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int, session: AsyncSession = Depends(get_session)):
    author = await author_service.get_author(session, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@author_router.post("/", response_model=AuthorResponse, status_code=201)
async def add_author(author: AuthorCreate, session: AsyncSession = Depends(get_session)):
    return await author_service.add_author(session, author)

@author_router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(author_id: int, author_update: AuthorCreate, session: AsyncSession = Depends(get_session)):
    return await author_service.update_author(session, author_id, author_update)

@author_router.delete("/{author_id}", status_code=204)
async def delete_author(author_id: int, session: AsyncSession = Depends(get_session)):
    deleted_author = await author_service.delete_author(session, author_id)
    if deleted_author is None:
        raise HTTPException(status_code=404, detail="Author not found")

