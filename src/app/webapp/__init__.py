__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/webapp", tags=["WebApp"])

# Register all schemas and routes
import src.app.webapp.routes  # noqa: E402, F401
