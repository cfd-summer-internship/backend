from settings import get_settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

settings = get_settings()
engine=create_async_engine(settings.connection_string,echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    """Create an asynchronous local database session"""
    async with AsyncSessionLocal() as session:
        yield session