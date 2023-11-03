__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/actions", tags=["Actions"])

# Register all schemas and routes
import src.app.actions.routes  # noqa: E402, F401
