![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Nginx](https://img.shields.io/badge/Nginx-reverse--proxy?style=for-the-badge&logo=nginx)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-yellow?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-grey?style=for-the-badge&logo=telegram)


# Проект: Бэкенд для умной метеостанции

Серверная часть умной метеостанции — REST API на FastAPI с PostgreSQL, интеграцией с Telegram и визуализацией данных с устройств

## Репозитории проекта

- [meteostation-firmware](https://github.com/finstape/meteostation-firmware) — код Arduino + ESP (отправка данных)
- [meteostation-backend](https://github.com/finstape/meteostation-backend) — backend-сервер (**этот репозиторий**)
- [meteostation-ml](https://github.com/finstape/meteostation-ml) — ML-модель прогнозирования температуры и осадков

## Архитектура

- **FastAPI** — веб-сервер и REST API
- **PostgreSQL** — база данных настроек и показаний
- **Alembic** — миграции схемы
- **Telegram Bot (aiogram)** — командами /start, /weather, /predict, /plot и т.д.
- **Docker Compose** — контейнеризация и развёртывание
- **Nginx (reverse proxy)** — SSL, домен и проксирование

## Быстрый запуск через Docker

```bash
docker-compose up -d
```

Приложение будет доступно на `http://localhost:8000`, Swagger — `/swagger`

## Локальная разработка

1. Создать `.env` и установить переменные:

```bash
cp .env.example .env
```

2. Включить локальную БД (толко для создания миграций):
```env
USE_LOCAL_DB=1
```

3. Установить зависимости:
```bash
poetry install
poetry shell
```

4. Применить миграции:
```bash
make migrate
```

5. Для создания новых миграций:
```bash
make revision
```

## Полезные команды (локально)

```bash
make help          # Показать справку по командам
make env           # Создать .env на основе .env.example

make db            # Запустить сервер и базу через docker-compose
make run           # Запустить FastAPI-приложение локально
make open_db       # Зайти в контейнер с базой данных (psql)

make migrate       # Применить все миграции (alembic upgrade)
make revision      # Создать новую миграцию (autogenerate)
make upgrade       # Обновить БД до последней версии

make lint          # Проверить код через ruff
make format        # Отформатировать код (black + isort)

make clean         # Удалить временные и мусорные файлы
```

## Настройка Nginx (с SSL + webhook)

> ✅ Для продакшн-развёртывания

1. Установить SSL-сертификат (например, через Certbot: cert.pem и privkey.pem)
2. Прописать `telegram_webhook_url` в таблице `settings` или в админке
3. Добавить домен `yourdomain.com` в конфиг `nginx` и проксировать порт 8000:

```nginx
location / {
    proxy_pass http://localhost:8000;
    include proxy_params;
}
```

## Telegram Webhook

```bash
curl http://localhost:8000/api/v1/webhook/set
```

Команды:

- `/start` — приветствие
- `/weather` — текущая погода
- `/predict` — прогноз температуры и осадков
- `/plot [часы]` — график показаний (по умолчанию 6ч)
- `/settings [...]` — обновление настроек через JSON
- `/backup` — резервная копия базы данных

## Swagger и OpenAPI

- Swagger UI: `http://localhost:8000/swagger`
- OpenAPI JSON: `http://localhost:8000/openapi`

## Лицензия

Проект распространяется под лицензией **Apache License 2.0**.  
Разрешено свободное использование и модификация в образовательных и исследовательских целях
