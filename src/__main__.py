__all__ = ["app"]

import warnings

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api import docs
from src.api.routers import routers
from src.config import settings, Environment
from src.api.startup import setup_repositories
from src.prometheus import generate_prometheus_configs
from src.api.docs import generate_unique_operation_id

app = FastAPI(
    title=docs.TITLE,
    summary=docs.SUMMARY,
    description=docs.DESCRIPTION,
    version=docs.VERSION,
    contact=docs.CONTACT_INFO,
    license_info=docs.LICENSE_INFO,
    openapi_tags=docs.TAGS_INFO,
    servers=[
        {"url": settings.APP_ROOT_PATH, "description": "Current"},
    ],
    root_path=settings.APP_ROOT_PATH,
    root_path_in_servers=False,
    swagger_ui_oauth2_redirect_url=None,
    generate_unique_id_function=generate_unique_operation_id,
)

# CORS settings
if settings.CORS_ALLOW_ORIGINS:
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.SMTP_ENABLED:
    warnings.warn("SMTP and email connection is enabled!")
else:
    warnings.warn("SMTP and email connection is disabled!")


@app.on_event("startup")
async def startup_event():
    await setup_repositories()
    await generate_prometheus_configs()


@app.on_event("shutdown")
async def close_connection():
    from src.api.dependencies import Dependencies

    storage = Dependencies.get_storage()
    await storage.close_connection()


for router in routers:
    app.include_router(router)

if settings.ENVIRONMENT == Environment.DEVELOPMENT:
    import logging

    warnings.warn("SQLAlchemy logging is enabled!")
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
