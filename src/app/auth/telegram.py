import hashlib
import hmac

from pydantic import BaseModel

from src.config import settings


class TelegramWidgetData(BaseModel):
    hash: str
    query_id: str
    user: str
    auth_date: int

    @classmethod
    def parse_from_string(cls, string: str) -> "TelegramWidgetData":
        """
        Parse telegram widget data from string
        """
        from urllib.parse import parse_qs

        params = parse_qs(string)
        return cls(**{k: v[0] for k, v in params.items()})

    @property
    def string_to_hash(self) -> str:
        return "\n".join([f"{k}={getattr(self, k)}" for k in sorted(self.model_fields.keys()) if k != "hash"])

    @property
    def encoded(self) -> bytes:
        return self.string_to_hash.encode("utf-8").decode("unicode-escape").encode("ISO-8859-1")


def telegram_webapp_check_authorization(telegram_data: TelegramWidgetData) -> bool:
    """
    Verify telegram data

    https://core.telegram.org/widgets/login#checking-authorization
    """
    received_hash = telegram_data.hash
    encoded_telegarm_data = telegram_data.encoded
    token = settings.BOT_TOKEN.get_secret_value()
    secret_key = hmac.new("WebAppData".encode(), token.encode(), hashlib.sha256).digest()
    evaluated_hash = hmac.new(secret_key, encoded_telegarm_data, hashlib.sha256).hexdigest()

    return evaluated_hash == received_hash
