import asyncio
import os
import sys
import typer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

app = typer.Typer(help="SolarView CLI")

@app.command()
def init_db():
    import asyncio
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    
    async def _init_db():
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            typer.echo("Error: DATABASE_URL environment variable not set.")
            typer.echo("Please create a .env file with your database configuration.")
            return
        
        if db_url.startswith("postgresql+"):
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            db_name = parsed.path.lstrip('/')
            
            postgres_url = f"{parsed.scheme}://{parsed.netloc}/postgres"
            engine = create_async_engine(postgres_url, echo=True)
            
            try:
                async with engine.begin() as conn:
                    result = await conn.execute(
                        text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                        {"dbname": db_name}
                    )
                    if not result.scalar():
                        typer.echo(f"Creating database: {db_name}")
                        await conn.execute(
                            text(f"CREATE DATABASE {db_name}")
                        )
                    else:
                        typer.echo(f"Database {db_name} already exists.")
                
                from sqlalchemy.ext.asyncio import AsyncSession
                from sqlalchemy.orm import sessionmaker
                from sqlalchemy import create_engine
                
                sync_db_url = db_url.replace("asyncpg", "psycopg2")
                engine = create_engine(sync_db_url)
                
                from alembic.config import Config
                from alembic import command
                
                alembic_cfg = Config("alembic.ini")
                command.upgrade(alembic_cfg, "head")
                
                typer.echo("Database initialized successfully!")
                
            except Exception as e:
                typer.echo(f"Error initializing database: {e}", err=True)
                raise typer.Exit(1)
            finally:
                await engine.dispose()
    
    asyncio.run(_init_db())

@app.command()
@typer.argument("email")
@typer.argument("password")
def create_admin(email: str, password: str):
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async def _create_admin():
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.exc import SQLAlchemyError
        
        from src.solar_api.database.models import User
        from src.solar_api.domain.user_models import get_password_hash
        
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            typer.echo("Error: DATABASE_URL environment variable not set.")
            typer.echo("Please create a .env file with your database configuration.")
            return
        
        engine = create_async_engine(db_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        try:
            async with async_session() as session:
                result = await session.execute(select(User).where(User.email == email))
                existing_user = result.scalars().first()
                
                if existing_user:
                    existing_user.is_superuser = True
                    existing_user.is_active = True
                    existing_user.hashed_password = get_password_hash(password)
                    await session.commit()
                    typer.echo(f"Updated existing user {email} as admin.")
                else:
                    user = User(
                        email=email,
                        hashed_password=get_password_hash(password),
                        is_superuser=True,
                        is_active=True
                    )
                    session.add(user)
                    await session.commit()
                    typer.echo(f"Created admin user: {email}")
                
        except SQLAlchemyError as e:
            typer.echo(f"Database error: {e}", err=True)
            raise typer.Exit(1)
        finally:
            await engine.dispose()
    
    asyncio.run(_create_admin())

@app.command()
def run():
    import uvicorn
    uvicorn.run(
        "src.solar_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"]
    )

def main():
    app()

if __name__ == "__main__":
    main()
