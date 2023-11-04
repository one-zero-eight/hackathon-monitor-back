__all__ = ["oauth", "router"]

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth = OAuth()

# Register all OAuth applications and routes
import src.app.auth.common  # noqa: E402, F401
import src.app.auth.telegram  # noqa: E402, F401
import src.app.dependencies  # noqa: E402, F401
