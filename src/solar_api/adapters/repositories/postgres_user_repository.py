from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.solar_api.domain.user_models import UserCreate, UserUpdate, UserInDB
from src.solar_api.database.models import User as UserModel
from src.solar_api.application.ports.user_repository import UserRepositoryPort

class PostgresUserRepository(UserRepositoryPort):
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalars().first()
        return UserInDB.from_orm(user) if user else None
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalars().first()
        return UserInDB.from_orm(user) if user else None
    
    async def create(self, user: UserCreate) -> UserInDB:
        from ....domain.user_models import get_password_hash
        
        hashed_password = get_password_hash(user.password)
        db_user = UserModel(
            email=user.email,
            hashed_password=hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return UserInDB.from_orm(db_user)
    
    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        from ....domain.user_models import get_password_hash
        
        update_data = user_update.dict(exclude_unset=True)
        
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
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
        result = await self.db.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return [UserInDB.from_orm(user) for user in users]
    
    async def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        from ....domain.user_models import verify_password
        
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
