from ninja import NinjaAPI

from core.api import router as core_router
from core.startup_report.public.api import router as startup_report_router

api = NinjaAPI()

api.add_router('/', core_router)
api.add_router('/', startup_report_router)
