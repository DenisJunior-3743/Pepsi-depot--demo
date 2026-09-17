from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.registry import register_modules_and_permissions
from app.auth.router import router as auth_router
from app.core.config import settings
from app.dashboard.router import router as dashboard_router
from app.db.session import SessionLocal
from app.depot.router import router as depot_router
from app.factory.router import router as factory_router
from app.modules.admin.router import router as admin_router

app = FastAPI(title="Pepsi Depo Management ERP")

# Permissive for now (this is a demo project with the frontend still being
# built against an unknown set of dev/deploy origins) - tighten to an
# explicit allow-list of real frontend origins before this goes anywhere
# near production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(factory_router)
app.include_router(admin_router)
app.include_router(depot_router)
app.include_router(dashboard_router)
app.include_router(auth_router)

# Runs once, synchronously, at process import time - plain top-level code
# rather than an ASGI lifespan hook, since running this same DB work inside
# an async lifespan (with or without a threadpool) reproducibly hung app
# startup on this machine (Windows + this FastAPI/Starlette version).
_registration_db = SessionLocal()
try:
    register_modules_and_permissions(_registration_db)
finally:
    _registration_db.close()


@app.get("/")
def read_root():
    return {"status": "ok", "service": "pepsi-depo-api", "environment": settings.environment}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
