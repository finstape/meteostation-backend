from app.utils.queries.setting import get_setting_by_key, save_multiple_settings
from app.utils.queries.weather import (
    fetch_part_data,
    get_last_data,
    get_last_data_for_sensors,
    insert_sensor_data,
    save_external_weather,
)

__all__ = [
    "get_setting_by_key",
    "save_multiple_settings",
    "fetch_part_data",
    "get_last_data",
    "get_last_data_for_sensors",
    "insert_sensor_data",
    "save_external_weather",
]
