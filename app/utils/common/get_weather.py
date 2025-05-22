import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import WeatherUploadRequest
from app.utils.queries import (
    get_setting_by_key,
    insert_sensor_data,
    save_external_weather,
)


async def get_external_weather(session: AsyncSession) -> dict:
    """
    Fetches the current weather data from the wttr.in API
    based on latitude, longitude settings

    Args:
        session (AsyncSession): The database session

    Returns:
        Dict: A dictionary containing the weather description, feels like temperature,
              precipitation, UV index, and wind speed in m/s
    """

    lat = await get_setting_by_key(session, "latitude")
    lon = await get_setting_by_key(session, "longitude")

    url = f"http://wttr.in/{lat},{lon}?format=j1"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    current = data["current_condition"][0]

    # Parse the data
    description = current.get("lang_ru", [{"value": "Нет данных"}])[0]["value"]
    feels_like = current["FeelsLikeC"]
    precip_mm = current["precipMM"]
    uv_index = current["uvIndex"]
    wind_kmph = float(current["windspeedKmph"])
    wind_mps = round(wind_kmph / 3.6, 1)

    return {
        "weather_description": description,
        "temperature_feels_like": feels_like,
        "precipitation": precip_mm,
        "uv_index": uv_index,
        "wind_speed": wind_mps,
    }


async def new_data_logic(
    session: AsyncSession,
    payload: WeatherUploadRequest,
) -> None:
    """
    Handles the logic for inserting new sensor data and fetching external weather data

    Args:
        session (AsyncSession): The database session
        payload (WeatherUploadRequest): The payload containing sensor data
    """
    await insert_sensor_data(session, payload)

    external_weather = await get_external_weather(session)
    await save_external_weather(session, external_weather)
