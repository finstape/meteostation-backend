from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.queries import get_setting_by_key
from app.utils.telegram import handlers

bot: Bot | None = None
dp: Dispatcher | None = None


async def init_bot_and_dispatcher(session: AsyncSession) -> None:
    """
    Initialize the bot and dispatcher
    This function retrieves the Telegram bot token from the database and initializes
    """
    global bot, dp
    if bot is None or dp is None:
        TELEGRAM_BOT_TOKEN = await get_setting_by_key(session, "telegram_bot_token")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        dp = Dispatcher()

        dp.include_router(handlers.router)


def get_bot() -> Bot:
    """
    Get the initialized bot instance

    Returns:
        Bot: The initialized bot instance
    """
    if bot is None:
        raise ValueError("Bot is not initialized")
    return bot


def get_dispatcher() -> Dispatcher:
    """
    Get the initialized dispatcher instance

    Returns:
        Dispatcher: The initialized dispatcher instance
    """
    if dp is None:
        raise ValueError("Dispatcher is not initialized")
    return dp
