FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    postgresql-client

WORKDIR /app

RUN pip install --upgrade pip && pip install --upgrade setuptools
RUN pip install poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --only main

COPY . .
COPY .env.example .env

RUN chmod +x /app/docker/server-entrypoint.sh
