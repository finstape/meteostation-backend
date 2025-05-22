import os
import subprocess
import tempfile

from fastapi.responses import FileResponse

from app.config import get_settings


async def create_postgres_backup() -> FileResponse:
    """
    Create a backup of the PostgreSQL database using pg_dump installed in the container.

    Returns:
        FileResponse: The backup file
    """
    settings = get_settings()
    db_host = settings.POSTGRES_HOST
    db_name = settings.POSTGRES_DB
    db_user = settings.POSTGRES_USER
    db_port = settings.POSTGRES_PORT
    db_password = settings.POSTGRES_PASSWORD

    with tempfile.NamedTemporaryFile(delete=False, suffix=".sql") as tmp:
        dump_path = tmp.name

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password  # secure way to pass password

    result = subprocess.run(
        [
            "pg_dump",
            "-h",
            db_host,
            "-p",
            str(db_port),
            "-U",
            db_user,
            "-d",
            db_name,
            "-F",
            "plain",
            "-f",
            dump_path,
        ],
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError("pg_dump failed to create backup")

    return FileResponse(
        path=dump_path, filename="backup.sql", media_type="application/sql"
    )
