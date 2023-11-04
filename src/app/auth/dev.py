__all__ = []

from typing import Annotated

from src.config import settings, Environment
from src.repositories.users import AbstractUserRepository

enabled = settings.ENVIRONMENT == Environment.DEVELOPMENT

if enabled:
    if settings.JWT_ENABLED:
        import warnings
        from src.app.auth import router
        from src.app.auth.common import redirect_with_token, ensure_allowed_return_to
        from src.repositories.tokens import TokenRepository
        from src.schemas.users import CreateUser
        from src.app.dependencies import DEPENDS_USER_REPOSITORY

        warnings.warn(
            "Dev auth provider is enabled! "
            "Use this only for development environment "
            "(otherwise, set ENVIRONMENT=production)."
        )

        @router.get("/dev/login", include_in_schema=False)
        async def dev_login(
            telegram_id: int,
            user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
            return_to: str = "/",
            telegram_first_name="Alex",
        ):
            ensure_allowed_return_to(return_to)
            existing_user = await user_repository.read(telegram_id)

            if existing_user:
                token = TokenRepository.create_access_token(existing_user.telegram_id)
                return redirect_with_token(return_to, token)
            scheme = CreateUser(
                telegram_id=telegram_id,
                telegram_first_name=telegram_first_name,
            )

            user = await user_repository.create(user=scheme)
            token = TokenRepository.create_access_token(user.telegram_id)
            return redirect_with_token(return_to, token)

        @router.get("/dev/token")
        async def get_dev_token(
            user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
            telegram_id: int,
            telegram_first_name="Alex",
        ) -> str:
            existing_user = await user_repository.read(telegram_id)
            if existing_user:
                return TokenRepository.create_access_token(existing_user.telegram_id)
            scheme = CreateUser(
                telegram_id=telegram_id,
                telegram_first_name=telegram_first_name,
            )
            user = await user_repository.create(user=scheme)
            return TokenRepository.create_access_token(user.telegram_id)
