from app.endpoints.setting import api_router as get_setting_router
from app.endpoints.weather import api_router as get_weather_router
from app.endpoints.telegram import api_router as get_telegram_router

list_of_routes = [
    get_weather_router,
    get_setting_router,
    get_telegram_router,
]


__all__ = [
    "list_of_routes",
]
