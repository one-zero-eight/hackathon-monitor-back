__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Register all schemas and routes
import src.schemas.alerts  # noqa: E402, F401
import src.app.alerts.routes  # noqa: E402, F401
