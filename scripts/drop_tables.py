import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Get database URL from environment
DEFAULT_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/solarview"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Handle database URL for asyncpg
if "+asyncpg" not in DATABASE_URL:
    if "postgresql://" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    elif "postgres://" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")

# Remove any SSL parameters from the URL
if "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]


async def drop_all_objects():
    # Create the engine with minimal configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"server_settings": {"application_name": "solarview_cleanup"}},
    )

    async with engine.begin() as conn:
        try:
            # First, drop all foreign key constraints
            print("\nDropping foreign key constraints...")
            await conn.execute(
                text("""
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (
                        SELECT 'ALTER TABLE ' || quote_ident(n.nspname) || '.' || 
                               quote_ident(t.relname) || ' DROP CONSTRAINT ' || 
                               quote_ident(conname) || ' CASCADE' AS drop_command
                        FROM pg_constraint c
                        JOIN pg_class t ON c.conrelid = t.oid
                        JOIN pg_namespace n ON t.relnamespace = n.oid
                        WHERE c.contype = 'f' 
                        AND n.nspname = 'public'
                    ) LOOP
                        EXECUTE r.drop_command;
                    END LOOP;
                END $$;
            """)
            )

            # Drop all tables
            print("\nDropping tables...")
            tables = await conn.execute(
                text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    AND tablename NOT LIKE 'pg_%'
                    AND tablename NOT LIKE 'sql_%'
                """)
            )

            for table in tables:
                try:
                    print(f"Dropping table: {table[0]}")
                    await conn.execute(
                        text(f'DROP TABLE IF EXISTS "{table[0]}" CASCADE')
                    )
                except Exception as e:
                    print(f"Error dropping table {table[0]}: {e}")

            # Drop all sequences
            print("\nDropping sequences...")
            sequences = await conn.execute(
                text("""
                    SELECT sequence_name 
                    FROM information_schema.sequences 
                    WHERE sequence_schema = 'public'
                """)
            )

            for seq in sequences:
                try:
                    print(f"Dropping sequence: {seq[0]}")
                    await conn.execute(
                        text(f'DROP SEQUENCE IF EXISTS "{seq[0]}" CASCADE')
                    )
                except Exception as e:
                    print(f"Error dropping sequence {seq[0]}: {e}")

            # Drop all types
            print("\nDropping custom types...")
            types = await conn.execute(
                text("""
                    SELECT typname 
                    FROM pg_type t 
                    JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
                    WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid)) 
                    AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
                    AND n.nspname = 'public'
                """)
            )

            for type_ in types:
                try:
                    print(f"Dropping type: {type_[0]}")
                    await conn.execute(
                        text(f'DROP TYPE IF EXISTS "{type_[0]}" CASCADE')
                    )
                except Exception as e:
                    print(f"Error dropping type {type_[0]}: {e}")

            print("\nDatabase cleanup completed successfully!")

        except Exception as e:
            print(f"\nError during database cleanup: {e}")
            await conn.rollback()
            raise
        finally:
            await conn.close()


if __name__ == "__main__":
    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable is not set")
        exit(1)

    print("""
     WARNING: This will drop ALL database objects including:
    - Tables
    - Sequences
    - Custom types
    - And all dependent objects (CASCADE)
    """)

    confirm = input(
        "\nAre you sure you want to continue? This operation cannot be undone! (y/n): "
    )

    if confirm.lower() == "y":
        try:
            asyncio.run(drop_all_objects())
        except Exception as e:
            print(f"\nError: {e}")
            exit(1)
    else:
        print("\nOperation cancelled")
