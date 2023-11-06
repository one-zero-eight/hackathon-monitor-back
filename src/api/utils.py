from src.api.exceptions import NotEnoughPermissionsException
from src.config import Target
from src.modules.auth.schemas import VerificationResult


def permission_check(_verification: VerificationResult, target: Target):
    if _verification.user_id is None:
        return

    if _verification.user_id not in target.ADMINS:
        raise NotEnoughPermissionsException()
