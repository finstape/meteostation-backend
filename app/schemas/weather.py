from pydantic import BaseModel, Field


class SensorData(BaseModel):
    temperature: float = Field(..., title="Sensor temperature")
    humidity: float = Field(..., title="Sensor humidity")
    pressure: float = Field(..., title="Sensor pressure")

    class Config:
        from_attributes = True


class CentralData(SensorData):
    co2: int = Field(..., title="Sensor CO2 level")
    tvoc: int = Field(..., title="Sensor TVOC level")

    class Config:
        from_attributes = True


class ExternalData(BaseModel):
    weather_description: str = Field(..., title="Weather description")
    temperature_feels_like: float = Field(..., title="Feels like temperature")
    precipitation: float = Field(..., title="Precipitation")
    uv_index: float = Field(..., title="UV index")
    wind_speed: float = Field(..., title="Wind speed")

    class Config:
        from_attributes = True


class WeatherCurrentResponse(BaseModel):
    central: CentralData
    outdoor: SensorData
    external_weather: ExternalData


class WeatherPredictionResponse(BaseModel):
    predicted_temp: float = Field(..., title="Predicted temperature")
    predicted_rain: bool = Field(..., title="Predicted rain")


class WeatherUploadRequest(BaseModel):
    central: CentralData
    outdoor: SensorData

    class Config:
        from_attributes = True
