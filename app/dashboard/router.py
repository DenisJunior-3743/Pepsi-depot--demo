from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dashboard.schemas import SummaryResponse
from app.dashboard.services import build_summary
from app.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    return build_summary(db)
