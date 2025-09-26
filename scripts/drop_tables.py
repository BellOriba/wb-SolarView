import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/solarview")

if "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

async def clear_tables():
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"server_settings": {"application_name": "solarview_cleanup"}},
    )

    async with engine.begin() as conn:
        try:
            print("Starting database cleanup...")
            
            tables = ["panel_models", "users"]
            
            for table in tables:
                print(f"Clearing table: {table}")
                try:
                    await conn.execute(text('SAVEPOINT table_cleanup'))
                    try:
                        await conn.execute(text(f'TRUNCATE TABLE {table} CASCADE;'))
                        await conn.execute(text('RELEASE SAVEPOINT table_cleanup'))
                    except Exception as e:
                        await conn.execute(text('ROLLBACK TO SAVEPOINT table_cleanup'))
                        print(f"  Could not use TRUNCATE on {table}: {str(e).split('\n')[0]}")
                        print("  Trying DELETE instead...")
                        await conn.execute(text(f'DELETE FROM {table};'))
                        await conn.execute(text('RELEASE SAVEPOINT table_cleanup'))
                except Exception as e:
                    print(f"  Error clearing {table}: {str(e).split('\n')[0]}")
                    print("  Continuing with next table...")
            
            print("\nSuccessfully cleared tables:", ", ".join(tables))
            
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

    print("\nWARNING: This will clear all data from the following tables:")
    print("- panel_models")
    print("- users")
    print("\nThis operation cannot be undone!")

    confirm = input("\nAre you sure you want to continue? (y/n): ")

    if confirm.lower() == "y":
        try:
            asyncio.run(clear_tables())
            print("\nDatabase cleanup completed successfully!")
        except Exception as e:
            print(f"\nError: {e}")
            exit(1)
    else:
        print("\nOperation cancelled")