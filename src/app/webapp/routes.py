from typing import Annotated

from src.app.webapp import router
from src.app.dependencies import DEPENDS_WEBAPP


@router.get("/check-auth", responses={200: {"description": "Check auth"}})
async def check_auth(webapp: Annotated[bool, DEPENDS_WEBAPP]):
    return {"success": webapp}