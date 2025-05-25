from aiogram.types import Update
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.connection import get_session
from app.utils.queries import get_setting_by_key
from app.utils.telegram import get_bot, get_dispatcher, init_bot_and_dispatcher

api_router = APIRouter(tags=["Telegram"])


@api_router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    description="Endpoint for handling Telegram requests",
)
async def webhook_handler(
    request: Request,
):
    """ """
    data = await request.json()
    bot = get_bot()
    dp = get_dispatcher()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@api_router.get(
    "/webhook/set",
    status_code=status.HTTP_200_OK,
    description="Set Telegram webhook URL",
)
async def set_webhook(
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """
    Set Telegram webhook URL using the provided URL from the database.

    Raises:
        HTTPException: If setting the webhook fails (HTTP 400)
    """
    await init_bot_and_dispatcher(session)
    bot = get_bot()

    webhook_url = await get_setting_by_key(session, "telegram_webhook_url")
    success = await bot.set_webhook(webhook_url)

    if success:
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Webhook setting failed"
    )
