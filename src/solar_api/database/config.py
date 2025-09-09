import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from typing import Any, Dict, Optional, AsyncGenerator
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

DEFAULT_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/solarview"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

if "+asyncpg" not in DATABASE_URL:
    if "postgresql://" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    elif "postgres://" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    poolclass=NullPool
)
async_session_factory = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

async def create_tables(engine: AsyncEngine) -> None:
    from sqlalchemy import text
    
    async with engine.begin() as conn:
        await conn.execute(text("COMMIT"))
        try:
            await conn.execute(text(f"CREATE DATABASE solarview"))
        except Exception:
            pass
        
        from .models import Base
        await conn.run_sync(Base.metadata.create_all)

def get_db_sync():
    from sqlalchemy.orm import sessionmaker as sync_sessionmaker
    from sqlalchemy import create_engine as create_sync_engine
    
    sync_engine = create_sync_engine(
        DATABASE_URL.replace("postgresql+asyncpg", "postgresql"),
        echo=True,
    )
    SessionLocal = sync_sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

async def init_db() -> None:
    await create_tables(engine)
    
    from .initial_data import init_database
    async with async_session_factory() as session:
        await init_database(session)
