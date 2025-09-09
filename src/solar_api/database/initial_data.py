import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.solar_api.database.models import User
from src.solar_api.domain.user_models import get_password_hash

load_dotenv(project_root / '.env')

async def init_admin_user(db: AsyncSession) -> None:
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_email or not admin_password:
        print("Admin email or password not set in environment variables. Skipping admin user creation.")
        return
    
    result = await db.execute(select(User).where(User.email == admin_email))
    existing_admin = result.scalars().first()
    
    if existing_admin:
        print(f"Admin user {admin_email} already exists.")
        return
    
    admin_user = User(
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        is_active=True,
        is_superuser=True
    )
    
    db.add(admin_user)
    await db.commit()
    print(f"Created admin user: {admin_email}")

async def init_database(db: AsyncSession) -> None:
    await init_admin_user(db)
