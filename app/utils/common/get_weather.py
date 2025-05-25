import io
import math

from datetime import datetime, timedelta

import httpx
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Central, ExternalWeather, Outdoor
from app.schemas import WeatherUploadRequest
from app.utils.queries import (
    fetch_part_data,
    get_setting_by_key,
    insert_sensor_data,
    save_external_weather,
)
from app.utils.telegram import get_bot

WEATHER_CODES = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Туман с изморозью",
    51: "Лёгкая морось",
    53: "Морось",
    55: "Сильная морось",
    61: "Небольшой дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    71: "Небольшой снег",
    73: "Снег",
    75: "Сильный снег",
    80: "Кратковременные ливни",
    95: "Гроза",
    96: "Гроза с мелким градом",
    99: "Гроза с сильным градом",
}


def find_nearest_hour_index(time_list):
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    now_hour = now.isoformat()[:13]  # "2025-05-23T19"
    for i, t in enumerate(time_list):
        if t.startswith(now_hour):
            return i
    return -1


async def get_external_weather(session: AsyncSession) -> dict:
    """
    Fetches the current weather data from the open-meteo.com API
    based on latitude, longitude settings

    Args:
        session (AsyncSession): The database session

    Returns:
        Dict: A dictionary containing the weather description, feels like temperature,
              precipitation, UV index, and wind speed in m/s
    """
    lat = await get_setting_by_key(session, "latitude")
    lon = await get_setting_by_key(session, "longitude")

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=apparent_temperature,precipitation,uv_index"
        f"&timezone=UTC"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        data = response.json()

    current = data.get("current_weather", {})
    hourly = data.get("hourly", {})
    time_list = hourly.get("time", [])

    index = find_nearest_hour_index(time_list)

    def get_hourly_value(key):
        if index >= 0 and key in hourly:
            return hourly[key][index]
        return None

    return {
        "weather_description": WEATHER_CODES.get(
            current.get("weathercode"), "Нет данных"
        ),
        "temperature_feels_like": get_hourly_value("apparent_temperature"),
        "precipitation": get_hourly_value("precipitation"),
        "uv_index": get_hourly_value("uv_index"),
        "wind_speed": current.get("windspeed"),
    }


async def new_data_logic(
    session: AsyncSession,
    payload: WeatherUploadRequest,
) -> None:
    """
    Handles the logic for inserting new sensor data and fetching external weather data
    Check if parameters are bigger than default values (co2, tvoc) and notifies the user

    Args:
        session (AsyncSession): The database session
        payload (WeatherUploadRequest): The payload containing sensor data
    """
    await insert_sensor_data(session, payload)

    tvoc_alert_threshold = await get_setting_by_key(session, "tvoc_alert_threshold")
    co2_alert_threshold = await get_setting_by_key(session, "co2_alert_threshold")

    if (
        payload.central.tvoc > tvoc_alert_threshold
        or payload.central.co2 > co2_alert_threshold
    ):
        admin_telegram_id = await get_setting_by_key(session, "telegram_admin_id")
        bot = get_bot()

        await bot.send_message(
            admin_telegram_id,
            f"⚠️ Внимание! Обнаружен высокий уровень загрязнения:\n"
            f"CO₂: {payload.central.co2} ppm\n"
            f"TVOC: {payload.central.tvoc} ppb",
        )

    external_weather = await get_external_weather(session)
    await save_external_weather(session, external_weather)


async def generate_weather_plot(session: AsyncSession, hours: int) -> StreamingResponse:
    """
    Generates a plot of the weather data for the last specified hours
    and returns it as a StreamingResponse

    Args:
        session (AsyncSession): The database session
        hours (int): The number of hours to plot data for

    Returns:
        StreamingResponse: A streaming response containing the plot image
    """
    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    # Получаем данные
    central_data = await fetch_part_data(session, Central, time_threshold)
    outdoor_data = await fetch_part_data(session, Outdoor, time_threshold)
    external_data = await fetch_part_data(session, ExternalWeather, time_threshold)

    if not (central_data or outdoor_data or external_data):
        raise ValueError("No valid data found")

    frames = []

    if central_data:
        df = pd.DataFrame(
            [
                {
                    "created_at": row.created_at,
                    "temperature": row.temperature,
                    "humidity": row.humidity,
                    "co2": row.co2,
                    "tvoc": row.tvoc,
                }
                for row in central_data
            ]
        )
        if not df.empty:
            df["source"] = "central"
            frames.append(df)

    if outdoor_data:
        df = pd.DataFrame(
            [
                {
                    "created_at": row.created_at,
                    "temperature": row.temperature,
                    "humidity": row.humidity,
                    "pressure": row.pressure,
                }
                for row in outdoor_data
            ]
        )
        if not df.empty:
            df["source"] = "outdoor"
            frames.append(df)

    if external_data:
        df = pd.DataFrame(
            [
                {
                    "created_at": row.created_at,
                    "temperature": row.temperature_feels_like,
                    "precipitation": row.precipitation,
                    "uv_index": row.uv_index,
                    "wind_speed": row.wind_speed,
                }
                for row in external_data
            ]
        )
        if not df.empty:
            df["source"] = "external"
            frames.append(df)

    if not frames:
        raise ValueError("Нет валидных данных с полем created_at")

    full_df = pd.concat(frames, ignore_index=True)
    full_df = full_df[full_df["created_at"].notnull()].copy()
    full_df["created_at"] = pd.to_datetime(full_df["created_at"])
    full_df = full_df.sort_values("created_at")
    full_df.set_index("created_at", inplace=True)

    for col in full_df.columns:
        if col != "source":
            full_df[col] = pd.to_numeric(full_df[col], errors="coerce")

    full_df["source"] = full_df["source"].astype("category")

    df = full_df.groupby("source", observed=True).resample("10min").mean().reset_index()

    parameters = [col for col in df.columns if col not in ("created_at", "source")]

    if not parameters:
        raise ValueError("Нет данных для отображения")

    sns.set(style="whitegrid")
    n = len(parameters)
    ncols = 2
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=(16, 4 * nrows), sharex=True
    )
    axes = axes.flatten()

    for ax, param in zip(axes, parameters, strict=False):
        sns.lineplot(data=df, x="created_at", y=param, hue="source", ax=ax)
        ax.set_title(f"{param} за последние {hours} ч.")
        ax.set_ylabel(param)
        ax.set_xlabel("Время")
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
