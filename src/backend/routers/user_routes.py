from typing import Optional
import src.backend.services.user_services as user_services
from src.backend.schemas.user_schemas import UserCreate, UserUpdate, UserResponse
from src.backend.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

user_router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)

@user_router.get("/", response_model=UserResponse)
async def get_users(session: AsyncSession = Depends(get_session)):
    return await user_services.get_users(session)

@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await user_services.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.post("/", response_model=UserResponse, status_code=201)
async def add_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    return await user_services.add_user(session, user)

@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int,user: UserUpdate, session: AsyncSession = Depends(get_session)):
    return await user_services.update_user(session, user_id , user)

@user_router.delete("/{user_id}", response_model=Optional[UserResponse])
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await user_services.delete_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


