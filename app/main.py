from fastapi import FastAPI

from app.core.config import settings
from app.dashboard.router import router as dashboard_router
from app.depot.router import router as depot_router
from app.factory.router import router as factory_router
from app.modules.admin.router import router as admin_router

app = FastAPI(title="Pepsi Depo Management ERP")
app.include_router(factory_router)
app.include_router(admin_router)
app.include_router(depot_router)
app.include_router(dashboard_router)


@app.get("/")
def read_root():
    return {"status": "ok", "service": "pepsi-depo-api", "environment": settings.environment}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
