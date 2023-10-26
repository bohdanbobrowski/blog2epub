from datetime import datetime
from pydantic import BaseModel


class HistoryEntry(BaseModel):
    url: str
    used: int = 0
    last: datetime = datetime.now(tz=None)
