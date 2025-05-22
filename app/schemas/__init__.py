from app.schemas.setting import SettingPatchWithKey
from app.schemas.weather import (
    CentralData,
    ExternalData,
    SensorData,
    SensorInterval,
    WeatherCurrentResponse,
    WeatherPredictionResponse,
    WeatherUploadRequest,
)

__all__ = [
    "SettingPatchWithKey",
    "SensorData",
    "CentralData",
    "ExternalData",
    "WeatherCurrentResponse",
    "WeatherPredictionResponse",
    "WeatherUploadRequest",
    "SensorInterval",
]
