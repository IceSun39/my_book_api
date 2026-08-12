from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from src.backend.models.user import User
from src.backend.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from src.backend.core.security import get_password_hash


async def add_user(session: AsyncSession, user_create: UserCreate) -> UserResponse:
    hashed_password = get_password_hash(user_create.password)

    user_data = user_create.model_dump(exclude={"password"})

    new_user = User(
        **user_data,
        hashed_password=hashed_password,
        is_admin=False
    )

    session.add(new_user)
    await session.commit()
    stmt = select(User).where(User.user_id == new_user.user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    complete_user = result.scalar_one()

    return UserResponse.model_validate(complete_user)

async def update_user(session: AsyncSession, user_id: int,user_update: UserUpdate) -> UserResponse:
    stmt = select(User).where(User.user_id == user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        raw_password = update_data.pop("password")
        user.hashed_password = get_password_hash(raw_password)

    for key, value in update_data.items():
        setattr(user, key, value)


    await session.commit()
    await session.refresh(user)
    return UserResponse.model_validate(user)


async def delete_user(session: AsyncSession, user_id: int) -> Optional[UserResponse]:
    stmt = select(User).where(User.user_id == user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user is None:
        return None

    await session.delete(existing_user)
    await session.commit()
    return UserResponse.model_validate(existing_user)

async def get_user(session: AsyncSession, user_id: int) -> Optional[UserResponse]:
    stmt = select(User).where(User.user_id == user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        return None

    return UserResponse.model_validate(existing_user)


async def get_all_users(session: AsyncSession) -> List[UserResponse]:
    stmt = select(User).order_by(User.user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    existing_users = result.scalars().all()

    return [UserResponse.model_validate(user) for user in existing_users]


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)

    return result.scalars().one_or_none()