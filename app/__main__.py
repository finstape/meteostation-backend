from logging import getLogger

from fastapi import FastAPI
from uvicorn import run

from app.config import DefaultSettings
from app.config.utils import get_settings
from app.endpoints import list_of_routes
from app.utils.common import get_hostname

logger = getLogger(__name__)


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application
    """
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


def get_app() -> FastAPI:
    """
    Creates application and all dependable objects
    """
    description = "REST API бэкенд части умной метеостанции"

    application = FastAPI(
        title="Умная метеостанция",
        description=description,
        docs_url="/swagger",
        openapi_url="/openapi",
        version="0.1.0",
    )
    settings = get_settings()
    bind_routes(application, settings)
    application.state.settings = settings
    return application


app = get_app()


if __name__ == "__main__":  # pragma: no cover
    settings_for_application = get_settings()
    run(
        "app.__main__:app",
        host=get_hostname(settings_for_application.APP_HOST),
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=["app"],
        log_level="debug",
    )
