#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from src.solar_api.database.models import Base, User
from src.solar_api.domain.user_models import get_password_hash

from dotenv import load_dotenv

load_dotenv()


async def create_database_if_not_exists():
    db_url = os.getenv("DATABASE_URL")
    if not db_url or not db_url.startswith("postgresql"):
        return

    from urllib.parse import urlparse

    parsed = urlparse(db_url)
    db_name = parsed.path.lstrip("/")
    postgres_url = f"{parsed.scheme}://{parsed.netloc}/postgres"
    engine = create_async_engine(postgres_url, echo=True)

    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": db_name},
            )
            if not result.scalar():
                print(f"Creating database: {db_name}")
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
            else:
                print(f"Database {db_name} already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        await engine.dispose()


async def create_tables():
    from src.solar_api.database.config import engine

    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")


async def create_admin_user(email: str, password: str):
    from src.solar_api.database.config import async_session_factory

    async with async_session_factory() as session:
        result = await session.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": email}
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"Admin user {email} already exists. Updating password...")
            await session.execute(
                text("""
                    UPDATE users 
                    SET hashed_password = :hashed_password,
                        is_admin = TRUE,
                        is_active = TRUE
                    WHERE id = :id
                """),
                {"id": existing_user, "hashed_password": get_password_hash(password)},
            )
            print(f"Updated admin user {email}.")
        else:
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                is_admin=True,
                is_active=True,
            )
            session.add(user)
            print(f"Created admin user: {email}")

        await session.commit()


async def main():
    if len(sys.argv) > 2:
        admin_email = sys.argv[1]
        admin_password = sys.argv[2]
    else:
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        print(
            "Error: Admin email and password must be provided either as arguments or in the .env file."
        )
        print("Usage: python scripts/init_db.py [admin_email] [admin_password]")
        sys.exit(1)

    try:
        await create_database_if_not_exists()
        await create_tables()

        await create_admin_user(admin_email, admin_password)

        print("\nDatabase initialization complete!")
        print(f"Admin user: {admin_email}")

    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
