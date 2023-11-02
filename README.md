# FSP Hackathon 2023

## Development

1. Copy `.env.example` to `.env` and edit values if needed.
2. Run `openssl genrsa -out private.pem 2048` to generate private key for JWT signing.
3. Run `openssl rsa -in private.pem -pubout -out public.pem` to generate public key for JWT verification.
4. Run `poetry install` to install dependencies.
5. Run `poetry run pre-commit install` to set up pre-commit hooks.
6. Run `docker compose up -d db` to start Postgres database.
7. Run `poetry run alembic upgrade head` to run database migrations.
8. Run `poetry run uvicorn src.__main__:app --reload` to start the development server.
9. Go to http://127.0.0.1:8000/docs to see the API documentation.
