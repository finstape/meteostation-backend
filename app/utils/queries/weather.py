from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from app.db.models import Central, ExternalWeather, Outdoor


async def get_last_data(
    session: AsyncSession, model: type[DeclarativeMeta]
) -> DeclarativeMeta | None:
    """
    Fetch the last row from the table based on the highest id value

    Args:
        session (AsyncSession): The database session
        model (Type[DeclarativeMeta]): The SQLAlchemy model representing the table

    Returns:
        Sequence: The last row of the table as a model instance,
                  or None if the table is empty
    """
    query = select(model).order_by(desc(model.id)).limit(1)
    result = await session.execute(query)
    return result.scalars().first()


async def get_last_data_for_sensors(
    session: AsyncSession,
) -> dict[Any, DeclarativeMeta | None]:
    """
    Fetch the last row for each model in the predefined list of models.

    Args:
        session (AsyncSession): The database session.

    Returns:
        dict[str, list]: A dictionary where keys are table names and values
                         are the last rows of the respective tables
    """
    result = {}
    models = [Central, Outdoor, ExternalWeather]
    for model in models:
        result[model.__tablename__] = await get_last_data(session, model)
    print(result)
    return result
