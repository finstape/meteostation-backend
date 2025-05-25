from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:
        return sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def refresh(self) -> None:
        self.engine = create_async_engine(
            get_settings().database_uri,
            echo=True,
            future=True,
        )


async def get_session() -> AsyncSession:
    session_maker = SessionManager().get_session_maker()
    async with session_maker() as session:
        yield session


@asynccontextmanager
async def session_context():
    """
    A context manager for getting AsyncSession manually (used outside FastAPI, e.g. in aiogram handlers)
    """
    gen = get_session()
    session = await gen.__anext__()
    try:
        yield session
    finally:
        await session.aclose()


__all__ = [
    "get_session",
    "session_context",
]
