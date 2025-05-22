from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.connection import get_session
from app.schemas import SettingPatchWithKey
from app.utils.queries import save_multiple_settings

api_router = APIRouter(tags=["Setting"])


@api_router.patch(
    "/settings",
    status_code=status.HTTP_200_OK,
    description="Upload data from sensors (central, outdoor, external)",
)
async def patch_multiple_settings(
    payload: list[SettingPatchWithKey],
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """
    Update multiple settings in the database

    Args:
        payload (List[SettingPatchWithKey]): List of settings to update
        session (AsyncSession): The database session
    """
    await save_multiple_settings(session, payload)
    return
