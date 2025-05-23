from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.connection import get_session
from app.schemas import (
    CentralData,
    ExternalData,
    SensorData,
    SensorInterval,
    WeatherCurrentResponse,
    WeatherPredictionResponse,
    WeatherUploadRequest,
)
from app.utils.common import generate_weather_plot, new_data_logic
from app.utils.queries import get_last_data_for_sensors, get_setting_by_key
from app.utils.weather_predict import get_data_weather_prediction

api_router = APIRouter(tags=["Weather"])


@api_router.get(
    "/weather/current",
    status_code=status.HTTP_200_OK,
    response_model=WeatherCurrentResponse,
    description="Get current weather",
)
async def get_current_weather(
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """
    Get current weather data based on the last data

    Args:
        session (AsyncSession): The database session
    """
    raw_data = await get_last_data_for_sensors(session)

    formatted_data = {
        "central": CentralData.model_validate(raw_data["central"]),
        "outdoor": SensorData.model_validate(raw_data["outdoor"]),
        "external_weather": ExternalData.model_validate(raw_data["external_weather"]),
    }

    return WeatherCurrentResponse(**formatted_data)


@api_router.get(
    "/weather/predict",
    status_code=status.HTTP_200_OK,
    response_model=WeatherPredictionResponse,
    description="Get weather prediction",
)
async def get_weather_prediction(
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """
    Get weather prediction based on the last data

    Args:
        session (AsyncSession): The database session
    """
    data = await get_data_weather_prediction(session)
    return WeatherPredictionResponse(**data)


@api_router.post(
    "/weather/upload",
    status_code=status.HTTP_200_OK,
    description="Upload data from sensors (central, outdoor, external)",
)
async def upload_weather_data(
    payload: WeatherUploadRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """
    Upload weather data to the database

    Args:
        payload (WeatherUploadRequest): The data to be uploaded
        session (AsyncSession): The database session
    """
    await new_data_logic(session=session, payload=payload)
    return


@api_router.get(
    "/weather/interval",
    status_code=status.HTTP_200_OK,
    response_model=SensorInterval,
    description="Get interval for sensor polling",
)
async def get_sensor_poll_interval(
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    """
    Get the interval for sensor polling

    Args:
        session (AsyncSession): The database session
    """
    interval = await get_setting_by_key(session, "sensor_poll_interval_ms")
    return SensorInterval(sensor_poll_interval_ms=interval)


# TODO: implement telegram
# TODO: implement nginx


@api_router.get(
    "/weather/plot",
    status_code=status.HTTP_200_OK,
    response_class=StreamingResponse,
    description="Get plot of sensor data",
)
async def get_weather_plot(
    session: AsyncSession = Depends(get_session),  # noqa: B008
    hours: int = Query(6, ge=1, le=168),  # 1 hour - 7 days
):
    """
    Get a plot of sensor data for the last specified hours

    Args:
        session (AsyncSession): The database session
        hours (int): The number of hours to plot data for (default: 6, range: 1-168)
    """
    return await generate_weather_plot(session, hours)
