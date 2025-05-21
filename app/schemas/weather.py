from datetime import datetime

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    id: int = Field(..., title="Sensor data ID")
    temperature: float = Field(..., title="Sensor temperature")
    humidity: float = Field(..., title="Sensor humidity")
    pressure: float = Field(..., title="Sensor pressure")
    created_at: datetime = Field(..., title="Sensor timestamp")

    class Config:
        from_attributes = True


class CentralData(SensorData):
    co2: int = Field(..., title="Sensor CO2 level")
    tvoc: int = Field(..., title="Sensor TVOC level")

    class Config:
        from_attributes = True


class ExternalData(BaseModel):
    id: int = Field(..., title="External data ID")
    weather_description: str = Field(..., title="Weather description")
    temperature_feels_like: float = Field(..., title="Feels like temperature")
    precipitation: float = Field(..., title="Precipitation")
    uv_index: float = Field(..., title="UV index")
    wind_speed: float = Field(..., title="Wind speed")
    created_at: datetime = Field(..., title="External weather timestamp")

    class Config:
        from_attributes = True


class WeatherCurrentResponse(BaseModel):
    central: CentralData
    outdoor: SensorData
    external_weather: ExternalData


class WeatherPredictionResponse(BaseModel):
    predicted_temp: float = Field(..., title="Predicted temperature")
    predicted_rain: bool = Field(..., title="Predicted rain")
