from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Setting
from app.schemas import SettingPatchWithKey


async def get_setting_by_key(
    session: AsyncSession, key: str
) -> int | float | str | bool | None:
    """
    Get a setting value by its key and convert it to the specified type

    Args:
        session (AsyncSession): The database session
        key (str): The key of the setting to retrieve

    Returns:
        The value of the setting converted to its type if found, otherwise None
    """
    result = await session.execute(select(Setting).where(Setting.key == key))
    setting = result.scalars().first()

    if not setting:
        return None

    # Convert the value to the specified type
    if setting.type == "int":
        return int(setting.value)
    elif setting.type == "float":
        return float(setting.value)
    elif setting.type == "bool":
        return setting.value.lower() in ("true", "1", "yes")
    else:  # Default to string
        return setting.value


async def save_multiple_settings(
    session: AsyncSession,
    payload: list[SettingPatchWithKey],
) -> None:
    """
    Save multiple settings to the database

    Args:
        session (AsyncSession): The database session
        payload (List[SettingPatchWithKey]): List of settings to save
    """
    for item in payload:
        result = await session.execute(select(Setting).where(Setting.key == item.key))
        setting = result.scalars().first()
        if not setting:
            continue
        for field, value in item.model_dump(exclude_unset=True).items():
            if field != "key":
                setattr(setting, field, value)

    await session.commit()
