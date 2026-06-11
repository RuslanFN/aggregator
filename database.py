from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import dotenv
import os
dotenv.load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

db_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

session_maker = async_sessionmaker(create_async_engine(db_url))

async def get_session():
    async with session_maker() as session:
        yield session
