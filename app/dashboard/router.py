from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dashboard.schemas import SummaryResponse
from app.dashboard.services import build_summary
from app.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=SummaryResponse, dependencies=[Depends(get_current_user)])
def get_summary(db: Session = Depends(get_db)):
    return build_summary(db)
