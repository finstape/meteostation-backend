import json
import tempfile

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from app.db.connection import session_context
from app.schemas import SettingPatchWithKey
from app.utils.common import create_postgres_backup
from app.utils.queries import get_last_data_for_sensors, save_multiple_settings
from app.utils.weather_predict import get_data_weather_prediction

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    """Send welcome message and list of available commands"""
    await message.answer(
        "🌍 <b>Добро пожаловать в бота умной метеостанции!</b>\n\n"
        "Доступные команды:\n"
        "/help - Описание команд\n"
        "/weather - Текущая погода\n"
        "/predict - Прогноз погоды\n"
        "/plot - График погоды\n"
        "/backup - Резервная копия\n"
        "/settings - Изменить настройки\n",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Send detailed help message with command descriptions and settings info"""
    await message.answer(
        "Список команд:\n\n"
        "/start - Приветственное сообщение\n"
        "/help - Это сообщение с подсказками\n"
        "/weather - Получить текущую погоду\n"
        "/predict - Получить прогноз температуры и осадков\n"
        "/plot [n] - Построить график данных за n часов (по умолчанию 6)\n"
        "/backup - Скачать резервную копию настроек\n"
        "/settings <json> - Обновить несколько настроек\n\n"
        "Доступные ключи настроек:\n"
        "- latitude (float)\n"
        "- longitude (float)\n"
        "- sensor_poll_interval_ms (int)\n"
        "- co2_alert_threshold (int)\n"
        "- tvoc_alert_threshold (int)\n"
        "- telegram_bot_token (str)\n"
        "- telegram_webhook_url (str)\n\n"
        "Пример:\n"
        '/settings [{"key": "sensor_poll_interval_ms", "value": "60000", '
        '"type": "int"}]',
    )


@router.message(Command("weather"))
async def weather_handler(message: types.Message):
    """Fetch and display current weather data"""
    await message.answer("Получаю текущую погоду... ⌛")

    async with session_context() as session:
        weather = await get_last_data_for_sensors(session)

    text = (
        "<b>🌡 Центральные датчики:</b>\n"
        f"🌡 Температура: {weather['central'].temperature} °C\n"
        f"💧 Влажность: {weather['central'].humidity} %\n"
        f"📈 Давление: {weather['central'].pressure} мм рт.ст.\n"
        f"🫁 CO₂: {weather['central'].co2} ppm\n"
        f"🌫 TVOC: {weather['central'].tvoc} ppb\n\n"
        "<b>🌤 Уличные датчики:</b>\n"
        f"🌡 Температура: {weather['outdoor'].temperature} °C\n"
        f"💧 Влажность: {weather['outdoor'].humidity} %\n"
        f"📈 Давление: {weather['outdoor'].pressure} мм рт.ст.\n\n"
        "<b>🌍 Внешняя погода:</b>\n"
        f"☁️ Описание: {weather['external_weather'].weather_description}\n"
        f"🤔 Ощущается как: {weather['external_weather'].temperature_feels_like} °C\n"
        f"🌧 Осадки: {weather['external_weather'].precipitation} мм\n"
        f"🔆 УФ-индекс: {weather['external_weather'].uv_index}\n"
        f"💨 Скорость ветра: {weather['external_weather'].wind_speed} м/с"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("predict"))
async def predict_handler(message: types.Message):
    """Fetch and display predicted weather information"""
    await message.answer("Строю прогноз... ⛅")

    async with session_context() as session:
        predict = await get_data_weather_prediction(session)

    await message.answer(
        f"📡 <b>Прогноз погоды через 6ч:</b>\n\n"
        f"🌡 Температура: <b>{predict['predicted_temp']} °C</b>\n"
        f"🌧 Вероятность дождя: <b>{'Да ☔️' if predict['predicted_rain'] else 'Нет 🌤'}"
        "</b>",
        parse_mode="HTML",
    )


@router.message(Command("plot"))
async def plot_handler(message: types.Message):
    """Generate and send weather sensor data plot"""
    args = message.text.strip().split()
    try:
        hours = int(args[1]) if len(args) > 1 else 6
        if not (1 <= hours <= 168):
            raise ValueError
    except (IndexError, ValueError):
        await message.answer(
            "⚠️ Укажи количество часов от 1 до 168, например:\n/plot 24"
        )
        return

    await message.answer(f"Генерирую график за последние {hours} ч... 🔬")

    try:
        async with session_context() as session:
            from app.utils.common import generate_weather_plot

            response = await generate_weather_plot(session, hours)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            async for chunk in response.body_iterator:
                tmp.write(chunk)
            tmp.close()

        await message.answer_photo(
            photo=FSInputFile(tmp.name), caption=f"📈 График за последние {hours} ч."
        )

    except Exception as e:
        await message.answer(f"❌ Не удалось построить график: {e}")


@router.message(Command("backup"))
async def backup_handler(message: types.Message):
    """Create and send system settings backup"""
    await message.answer("Создаю резервную копию... 📁")

    try:
        file_response = await create_postgres_backup()
        file_path = file_response.path

        await message.answer_document(
            document=FSInputFile(file_path), caption="📄 Резервная копия базы данных"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании резервной копии: {e}")


@router.message(Command("settings"))
async def settings_handler(message: types.Message):
    """Parse JSON payload and send it to settings update endpoint"""
    text = message.text.removeprefix("/settings").strip()

    if not text:
        await message.answer(
            "Пожалуйста, передайте настройки в формате JSON, например:\n"
            "/settings [{\"key\": \"sensor_poll_interval_ms\", "
            "\"value\": 60000, \"type\": \"int\"}]"
        )
        return

    try:
        raw = json.loads(text)
        payload = [SettingPatchWithKey(**item) for item in raw]

        async with session_context() as session:
            await save_multiple_settings(session, payload)

        await message.answer("✅ Настройки успешно обновлены")

    except json.JSONDecodeError:
        await message.answer("❌ Ошибка: некорректный JSON")
    except Exception as e:
        await message.answer(f"❌ Ошибка применения настроек: {e}")


@router.message(F.text)
async def echo_text(message: types.Message):
    """Echo back any text message"""
    await message.answer(f"Ты написал: {message.text}")
