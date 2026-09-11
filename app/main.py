from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="Pepsi Depo Management ERP")


@app.get("/")
def read_root():
    return {"status": "ok", "service": "pepsi-depo-api", "environment": settings.environment}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
