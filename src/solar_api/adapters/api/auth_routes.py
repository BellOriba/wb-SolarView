from fastapi import APIRouter, Depends, HTTPException, status

from src.solar_api.domain.user_models import UserInDB
from src.solar_api.application.services.user_service import UserService
from src.solar_api.adapters.repositories import PostgresUserRepository
from src.solar_api.database import get_db
from src.solar_api.application.services.auth_service import get_current_user, get_admin_user

router = APIRouter(tags=["authentication"])

@router.post("/login", response_model=UserInDB)
async def login(
    email: str,
    password: str,
    db = Depends(get_db)
):
    user_repository = PostgresUserRepository(db)
    user_service = UserService(user_repository)
    
    user = await user_service.get_user_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    return user

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user

@router.post("/rotate-key", response_model=dict)
async def rotate_api_key(
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_db)
):
    user_repository = PostgresUserRepository(db)
    user_service = UserService(user_repository)
    
    new_key = await user_service.rotate_api_key(current_user.id, current_user)
    return {"api_key": new_key}

@router.post("/admin/rotate-key/{user_id}", response_model=dict)
async def rotate_user_api_key(
    user_id: int,
    admin_user: UserInDB = Depends(get_admin_user),
    db = Depends(get_db)
):
    user_repository = PostgresUserRepository(db)
    user_service = UserService(user_repository)
    
    new_key = await user_service.rotate_api_key(user_id, admin_user)
    return {"api_key": new_key}
