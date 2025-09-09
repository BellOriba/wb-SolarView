from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.solar_api.database import get_db
from src.solar_api.database.models import User
from src.solar_api.domain.user_models import UserInDB

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_api_key(self, api_key: str) -> Optional[UserInDB]:
        if not api_key:
            return None
            
        user = await self.db.execute(
            User.__table__.select().where(User.api_key == api_key)
        )
        user = user.fetchone()
        
        if not user:
            return None
            
        return UserInDB.from_orm(user)

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

async def get_current_user(
    api_key: str = Depends(API_KEY_HEADER),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInDB:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "API-Key"},
        )
    
    user = await auth_service.get_user_by_api_key(api_key)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    
    return user

async def get_admin_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user
