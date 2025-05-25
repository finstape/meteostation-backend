from aiogram import F, Router, types
from aiogram.filters.command import Command

router = Router()


@router.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer("Привет! Я бот метеостанции.")


@router.message(F.text)
async def echo_text(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")
