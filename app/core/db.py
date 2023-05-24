from sqlalchemy import Column, Integer  # type: ignore
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession, create_async_engine)
from sqlalchemy.orm import (  # type: ignore
    declared_attr, declarative_base, sessionmaker)

from app.core.config import settings


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
