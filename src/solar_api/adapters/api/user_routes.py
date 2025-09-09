from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.solar_api.domain.user_models import (
    UserCreate, 
    UserUpdate, 
    UserInDB, 
    UserResponse,
    UserInDB
)
from src.solar_api.application.services.user_service import UserService
from src.solar_api.adapters.repositories import PostgresUserRepository
from src.solar_api.database import get_db
from .dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db=Depends(get_db)) -> UserService:
    user_repository = PostgresUserRepository(db)
    return UserService(user_repository)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await user_service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.list_users(skip=skip, limit=limit, current_user=current_user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.update_user(user_id, user_update, current_user)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        success = await user_service.delete_user(user_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.post("/change-password/", status_code=status.HTTP_200_OK)
async def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
    current_user: UserInDB = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        success = await user_service.change_password(
            user_id=user_id,
            current_password=current_password,
            new_password=new_password,
            current_user=current_user
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"detail": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
