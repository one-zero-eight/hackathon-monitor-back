__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/views", tags=["Views"])

# Register all schemas and routes
import src.app.views.routes  # noqa: E402, F401
