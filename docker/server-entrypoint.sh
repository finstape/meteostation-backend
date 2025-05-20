#!/bin/sh

# Check if .env file exists
if [ -f /app/.env ]; then
    set -a
    source /app/.env
    set +a
else
    echo ".env file not found in /app directory"
    exit 1
fi

until cd /app
do
    echo "Waiting for server volume..."
done

# Function to check PostgreSQL availability
check_postgres() {
    python << END
import asyncio
import os
import sys
import asyncpg

async def check_connection():
    try:
        conn = await asyncpg.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
        )
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    sys.exit(0)

asyncio.run(check_connection())
END
}

# Wait for PostgreSQL to be available
until check_postgres
do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 2
done

alembic upgrade head

export PGPASSWORD=$POSTGRES_PASSWORD

poetry run uvicorn app.__main__:app --host 0.0.0.0 --port 8000 --reload
