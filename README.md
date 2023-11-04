
# FSP Хакатон 2023

## Разработка

### Требования

- Python 3.11
- Poetry
- Docker

### Как начать

1. Скопируйте и переименуйте `.env.example` в `.env` и отредактируйте значения при необходимости.
2. Запустите `poetry install`, чтобы установить зависимости.
3. Запустите `poetry run pre-commit install`, чтобы настроить pre-commit хуки.
4. Запустите `docker compose up -d db`, чтобы запустить базу данных Postgres.
5. Запустите `poetry run alembic upgrade head`, чтобы выполнить миграции базы данных.
6. Запустите `poetry run uvicorn src.__main__:app --reload`, чтобы запустить сервер разработки.
7. Перейдите по адресу http://127.0.0.1:8000/docs, чтобы увидеть документацию API.

### Как создавать миграции

1. Настройте соединение с базой данных в `alembic.ini`. Рекомендуется использовать драйвер sync.
2. Запустите `poetry run alembic revision --autogenerate -m "Название миграции"`, чтобы сгенерировать миграцию.
3. Запустите `poetry run alembic upgrade head`, чтобы применить миграцию.
4. Запустите `poetry run alembic downgrade -1`, чтобы откатить миграцию.
5. Запустите `poetry run alembic history`, чтобы увидеть историю миграций.
