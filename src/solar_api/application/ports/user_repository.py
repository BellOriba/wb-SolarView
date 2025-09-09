from typing import Optional, List, Dict, Any
from ...domain.user_models import UserInDB


class UserRepositoryPort:
    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        raise NotImplementedError

    async def get_by_api_key(self, api_key: str) -> Optional[UserInDB]:
        raise NotImplementedError

    async def create(self, user_data: Dict[str, Any]) -> UserInDB:
        raise NotImplementedError

    async def update(
        self, user_id: int, user_update: Dict[str, Any]
    ) -> Optional[UserInDB]:
        raise NotImplementedError

    async def delete(self, user_id: int) -> bool:
        raise NotImplementedError

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        raise NotImplementedError

    async def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        raise NotImplementedError
