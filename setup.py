from setuptools import setup, find_packages

setup(
    name="solarview",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        
        "sqlalchemy>=1.4.0",
        "asyncpg>=0.25.0",
        "aiosqlite>=0.17.0",
        "alembic>=1.7.0",
        
        "passlib[bcrypt]>=1.7.4",
        "python-jose[cryptography]>=3.3.0",
        "python-multipart>=0.0.5",
        
        "pydantic>=1.8.0",
        "httpx>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.0",
            "isort>=5.0.0",
            "mypy>=0.910",
            "flake8>=3.9.0",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "solarview=solar_api.cli:main",
        ],
    },
)
