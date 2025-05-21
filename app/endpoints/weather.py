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
)
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
    session: AsyncSession = Depends(get_session),
):
    raw_data = await get_last_data_for_sensors(session)

    formatted_data = {
        "central": CentralData.model_validate(raw_data["central"]),
        "outdoor": SensorData.model_validate(raw_data["outdoor"]),
        "external_weather": ExternalData.model_validate(raw_data["external_weather"]),
    }

    return WeatherCurrentResponse(**formatted_data)


@api_router.get(
    "weather/predict",
    status_code=status.HTTP_200_OK,
    response_model=WeatherPredictionResponse,
    description="Get weather prediction",
)
async def get_weather_prediction(
    session: AsyncSession = Depends(get_session),
):
    data = await get_data_weather_prediction(session)
    return WeatherPredictionResponse(**data)
