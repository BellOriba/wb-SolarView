import os
import logging
from pathlib import Path
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from sqlalchemy.schema import CreateTable, CreateIndex
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


def get_database_url() -> str:
    default_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/solarview"
    url = os.getenv("DATABASE_URL", default_url)

    if "+asyncpg" not in url:
        if "postgresql://" in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        elif "postgres://" in url:
            url = url.replace("postgres://", "postgresql+asyncpg://")

    return url.split("?")[0]


DATABASE_URL = get_database_url()


def create_db_engine(url: Optional[str] = None) -> AsyncEngine:
    db_url = url or DATABASE_URL
    logger.info(f"Creating database engine for: {db_url.split('@')[-1]}")

    return create_async_engine(
        db_url,
        echo=True,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "server_settings": {"application_name": "solarview_app", "timezone": "UTC"}
        },
    )


engine = create_db_engine()
async_session_factory = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def ensure_database_exists():
    import asyncpg
    from urllib.parse import urlparse

    parsed = urlparse(DATABASE_URL)
    db_name = parsed.path.lstrip("/")

    conn_params = {
        "user": parsed.username or "postgres",
        "password": parsed.password or "",
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": "postgres",
    }

    conn = None
    try:
        conn = await asyncpg.connect(**conn_params)

        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )

        if not exists:
            print(f"Creating database: {db_name}")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully")
        else:
            print(f"Database '{db_name}' already exists")

    except Exception as e:
        print(f"Error ensuring database exists: {e}")
        raise
    finally:
        if conn:
            await conn.close()


async def drop_tables(engine: AsyncEngine) -> None:
    from .models import Base
    from sqlalchemy.exc import SQLAlchemyError

    logger.info("Dropping all tables...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                """)
            )
            remaining_tables = [row[0] for row in result]

            if remaining_tables:
                logger.info(f"Dropping remaining tables: {', '.join(remaining_tables)}")
                for table in remaining_tables:
                    try:
                        await conn.execute(
                            text(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                        )
                    except Exception as e:
                        logger.warning(f"Error dropping table {table}: {e}")

            logger.info("Dropped all tables successfully")

    except SQLAlchemyError as e:
        logger.error(f"Error dropping tables: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in drop_tables: {e}")
        raise


async def create_tables(engine: AsyncEngine, drop_existing: bool = False) -> None:
    from .models import Base
    from sqlalchemy.exc import SQLAlchemyError

    logger.info("Starting table creation...")

    try:
        async with engine.begin() as conn:
            if drop_existing:
                logger.info("Dropping existing tables...")
                await drop_tables(engine)

            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                """)
            )
            existing_tables = {row[0] for row in result}

            for table_name, table in Base.metadata.tables.items():
                if table_name not in existing_tables:
                    try:
                        create_table_ddl = CreateTable(table).compile(engine)
                        await conn.execute(text(str(create_table_ddl).rstrip(";")))
                        logger.info(f"Created table: {table_name}")
                    except Exception as e:
                        if "already exists" not in str(e):
                            logger.warning(f"Error creating table {table_name}: {e}")
                            raise
                else:
                    logger.info(f"Table already exists: {table_name}")

            logger.info("Ensuring indexes exist...")
            for table in Base.metadata.tables.values():
                for index in table.indexes:
                    try:
                        index_exists = await conn.scalar(
                            text("""
                                SELECT 1 FROM pg_indexes 
                                WHERE schemaname = 'public' 
                                AND indexname = :index_name
                            """),
                            {"index_name": index.name},
                        )

                        if not index_exists:
                            create_index_ddl = CreateIndex(index).compile(engine)
                            await conn.execute(text(str(create_index_ddl)))
                            logger.info(f"Created index: {index.name}")
                        else:
                            logger.debug(f"Index already exists: {index.name}")

                    except Exception as e:
                        if "already exists" not in str(e):
                            logger.warning(f"Error creating index {index.name}: {e}")

            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
            )
            final_tables = [row[0] for row in result]

            if final_tables:
                logger.info(
                    f"Database contains {len(final_tables)} tables: {', '.join(final_tables)}"
                )
            else:
                logger.warning("No tables found in the database after creation attempt")

    except SQLAlchemyError as e:
        logger.error(f"Database error in create_tables: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_tables: {e}")
        raise


def get_db_sync():
    from sqlalchemy.orm import sessionmaker as sync_sessionmaker
    from sqlalchemy import create_engine as create_sync_engine

    sync_db_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")

    sync_engine = create_sync_engine(
        sync_db_url, echo=True, pool_pre_ping=True, pool_recycle=300
    )

    SessionLocal = sync_sessionmaker(
        autocommit=False, autoflush=False, bind=sync_engine
    )
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


async def init_db() -> None:
    logger.info("Starting database initialization...")

    try:
        logger.info("Ensuring database exists...")
        await ensure_database_exists()

        logger.info("Verificando e criando tabelas se necessário...")
        await create_tables(engine, drop_existing=False)

        try:
            from .initial_data import init_database

            logger.info("Loading initial data...")

            async with async_session_factory() as session:
                try:
                    await init_database(session)
                    logger.info("Initial data loaded successfully")
                except Exception as e:
                    logger.warning(f"Could not load initial data: {e}")
        except ImportError:
            logger.info("No initial data module found, skipping...")
        except Exception as e:
            logger.warning(f"Error loading initial data: {e}")

        try:
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """)
                )
                tables = [row[0] for row in result]
                logger.info(f"Database contains {len(tables)} tables")

                for table in tables:
                    try:
                        count_result = await conn.execute(
                            text(f'SELECT COUNT(*) FROM "{table}"')
                        )
                        count = count_result.scalar()
                        logger.debug(f"- {table}: {count} rows")
                    except Exception as count_error:
                        logger.debug(f"- {table}: Could not count rows - {count_error}")

        except Exception as e:
            logger.warning(f"Could not verify database state: {e}")

        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
