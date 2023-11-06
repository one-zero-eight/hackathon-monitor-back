from src.modules.actions.router import router as router_actions
from src.modules.alerts.router import router as router_alerts
from src.modules.pg.router import router as router_pg
from src.modules.users.router import router as router_users
from src.modules.views.router import router as router_views

routers = [router_users, router_pg, router_actions, router_alerts, router_views]

__all__ = ["routers"]
