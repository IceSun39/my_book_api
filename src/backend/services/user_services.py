from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from src.backend.models.user import User
from src.backend.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from src.backend.core.security import get_password_hash


async def _get_user_db(session: AsyncSession, user_id: int) -> User:
    """Шукає користувача в базі і повертає ORM-модель (або кидає 404)"""
    stmt = select(User).where(User.user_id == user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user(session: AsyncSession, user_id: int) -> UserResponse:
    user = await _get_user_db(session, user_id)
    return UserResponse.model_validate(user)


async def add_user(session: AsyncSession, user_create: UserCreate) -> UserResponse:
    existing_user = get_user_by_email(session, user_create.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exist")

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


async def update_user(session: AsyncSession, user_id: int, user_update: UserUpdate) -> UserResponse:
    user = await _get_user_db(session, user_id)

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        raw_password = update_data.pop("password")
        user.hashed_password = get_password_hash(raw_password)

    for key, value in update_data.items():
        setattr(user, key, value)

    await session.commit()
    
    complete_user = await _get_user_db(session, user_id)
    return UserResponse.model_validate(complete_user)


async def delete_user(session: AsyncSession, user_id: int) -> None:
    user = await _get_user_db(session, user_id)

    await session.delete(user)
    await session.commit()

    return None


async def get_all_users(session: AsyncSession) -> List[UserResponse]:
    stmt = select(User).order_by(User.user_id).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)
    existing_users = result.scalars().all()

    return [UserResponse.model_validate(user) for user in existing_users]


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email).options(selectinload(User.favorite_books))
    result = await session.execute(stmt)

    return result.scalars().one_or_none()
