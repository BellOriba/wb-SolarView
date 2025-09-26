from typing import Optional, List
from ...domain.user_models import UserCreate, UserUpdate, UserInDB, generate_api_key
from ...application.ports.user_repository import UserRepositoryPort
from ..security import pwd_context

class UserService:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    async def get_user(self, user_id: int) -> Optional[UserInDB]:
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        return await self.user_repository.get_by_email(email)

    async def get_user_by_api_key(self, api_key: str) -> Optional[UserInDB]:
        return await self.user_repository.get_by_api_key(api_key)

    async def create_user(self, user: UserCreate) -> UserInDB:
        existing_user = await self.user_repository.get_by_email(user.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_password = pwd_context.hash(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password
        user_data["api_key"] = generate_api_key()

        return await self.user_repository.create(user_data)

    async def update_user(
        self, user_id: int, user_update: UserUpdate, current_user: UserInDB
    ) -> Optional[UserInDB]:
        if user_id != current_user.id and not current_user.is_admin:
            raise ValueError("Not authorized to update this user")
        update_data = user_update.model_dump(exclude_unset=True)
        return await self.user_repository.update(user_id, update_data)

    async def delete_user(self, user_id: int, current_user: UserInDB) -> bool:
        if user_id != current_user.id and not current_user.is_admin:
            raise ValueError("Not authorized to delete this user")

        if user_id == current_user.id:
            raise ValueError("Cannot delete your own account")

        return await self.user_repository.delete(user_id)

    async def rotate_api_key(
        self, user_id: int, current_user: UserInDB
    ) -> Optional[str]:
        if user_id != current_user.id and not current_user.is_admin:
            raise ValueError("Not authorized to rotate this user's API key")

        new_api_key = generate_api_key()
        await self.user_repository.update(user_id, {"api_key": new_api_key})
        return new_api_key

    async def list_users(
        self, skip: int = 0, limit: int = 100, current_user: Optional[UserInDB] = None
    ) -> List[UserInDB]:
        if current_user and not current_user.is_admin:
            user = await self.user_repository.get_by_id(current_user.id)
            return [user] if user else []

        return await self.user_repository.list_users(skip=skip, limit=limit)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        return await self.user_repository.authenticate(email, password)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        current_user: UserInDB,
    ) -> bool:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if current_user.id != user_id and not current_user.is_admin:
            raise ValueError("Not authorized to change this user's password")

        if current_user.id == user_id:
            if not await self.user_repository.authenticate(
                user.email, current_password
            ):
                raise ValueError("Current password is incorrect")

        await self.user_repository.update(user_id, {"password": new_password})

        return True
