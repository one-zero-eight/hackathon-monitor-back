__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/pg", tags=["Postgres"])

# Register all schemas and routes
import src.schemas.users  # noqa: E402, F401
import src.app.users.routes  # noqa: E402, F401
