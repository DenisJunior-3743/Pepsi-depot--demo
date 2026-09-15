from datetime import datetime

from pydantic import BaseModel


class SummaryCard(BaseModel):
    key: str
    title: str
    value: float
    subtitle: str | None = None
    link: str


class SummaryResponse(BaseModel):
    generated_at: datetime
    cards: list[SummaryCard]
