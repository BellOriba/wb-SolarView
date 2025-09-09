import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.solar_api.database.models import User
from src.solar_api.domain.user_models import generate_api_key

load_dotenv(project_root / ".env")


async def init_admin_user(db: AsyncSession) -> bool:
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

        if not admin_email or not admin_password:
            print(
                "Warning: Using default admin credentials. Please set ADMIN_EMAIL and ADMIN_PASSWORD in .env file."
            )

        async with db.begin():
            result = await db.execute(select(User).where(User.email == admin_email))
            existing_admin = result.scalars().first()

            if existing_admin:
                print(f"Admin user {admin_email} already exists")
                return False

            admin_count = await db.scalar(select(User).where(User.is_admin))
            if admin_count is not None:
                print("Admin user already exists in the system")
                return False

            admin_user = User(
                email=admin_email,
                hashed_password=admin_password,
                api_key=generate_api_key(),
                is_active=True,
                is_admin=True,
            )

            db.add(admin_user)
            await db.commit()

            print(f"Created admin user: {admin_email}")
            print(f"API Key: {admin_user.api_key}")
            print("IMPORTANT: Save this API key securely as it won't be shown again!")

            return True

    except Exception as e:
        print(f"Error creating admin user: {e}")
        await db.rollback()
        raise


async def init_database(db: AsyncSession) -> None:
    try:
        print("Loading initial data...")
        await init_admin_user(db)
    except Exception as e:
        print(f"Warning: Could not load initial data: {e}")
