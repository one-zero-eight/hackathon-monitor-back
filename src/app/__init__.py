from src.app.users import router as router_users
from src.app.auth import router as router_auth
from src.app.pg import router as router_pg

routers = [router_users, router_auth, router_pg]

__all__ = ["routers"]
