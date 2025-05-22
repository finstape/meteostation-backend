from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.connection import get_session
from app.schemas import (
    CentralData,
    ExternalData,
    SensorData,
    WeatherCurrentResponse,
    WeatherPredictionResponse,
    WeatherUploadRequest,
)
from app.utils.common import new_data_logic
from app.utils.queries import get_last_data_for_sensors
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
