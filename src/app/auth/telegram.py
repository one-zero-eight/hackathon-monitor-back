import hashlib
import hmac
from typing import Optional

from pydantic import BaseModel

from src.config import settings


class TelegramWidgetData(BaseModel):
    hash: str
    id: int
    auth_date: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None

    @property
    def string_to_hash(self) -> str:
        return "\n".join(
            [
                f"{k}={getattr(self, k)}"
                for k in sorted(self.model_fields.keys())
                if k != "hash"
            ]
        )

    @property
    def encoded(self) -> bytes:
        return (
            self.string_to_hash.encode("utf-8")
            .decode("unicode-escape")
            .encode("ISO-8859-1")
        )


def telegram_check_authorization(
    telegram_data: TelegramWidgetData
) -> bool:
    """
    Verify telegram data

    https://core.telegram.org/widgets/login#checking-authorization
    """
    received_hash = telegram_data.hash
    encoded_telegarm_data = telegram_data.encoded
    secret_key: bytes = hashlib.sha256(settings.BOT_TOKEN.get_secret_value().encode("utf-8"))  # noqa: HL

    evaluated_hash = hmac.new(
        secret_key, encoded_telegarm_data, hashlib.sha256
    ).hexdigest()

    if evaluated_hash != received_hash:
        return False
    return True
