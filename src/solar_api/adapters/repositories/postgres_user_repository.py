from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.solar_api.adapters.api.dependencies import pwd_context
from src.solar_api.domain.user_models import UserInDB
from src.solar_api.database.models import User as UserModel
from src.solar_api.application.ports.user_repository import UserRepositoryPort


class PostgresUserRepository(UserRepositoryPort):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        result = await self.db.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalars().first()
        return UserInDB.from_orm(user) if user else None

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalars().first()
        return UserInDB.from_orm(user) if user else None

    async def get_by_api_key(self, api_key: str) -> Optional[UserInDB]:
        if not api_key:
            return None

        result = await self.db.execute(
            select(UserModel).where(UserModel.api_key == api_key)
        )
        user = result.scalars().first()
        return UserInDB.from_orm(user) if user else None

    async def create(self, user_data: Dict[str, Any]) -> UserInDB:
        db_user = UserModel(
            email=user_data["email"],
            password=user_data["password"],
            api_key=user_data["api_key"],
            is_active=user_data.get("is_active", True),
            is_admin=user_data.get("is_admin", False),
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return UserInDB.from_orm(db_user)

    async def update(
        self, user_id: int, user_update: Dict[str, Any]
    ) -> Optional[UserInDB]:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**user_update)
            .returning(UserModel)
        )

        result = await self.db.execute(stmt)
        updated_user = result.scalars().first()

        if updated_user:
            await self.db.commit()
            await self.db.refresh(updated_user)
            return UserInDB.from_orm(updated_user)

        return None

    async def delete(self, user_id: int) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        result = await self.db.execute(select(UserModel).offset(skip).limit(limit))
        users = result.scalars().all()
        return [UserInDB.from_orm(user) for user in users]

    async def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalars().first()

        if not user or not pwd_context.verify(password, user.password):
            return None
        
        if not user.is_active:
            return None

        return UserInDB.from_orm(user)
