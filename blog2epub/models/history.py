from dataclasses import dataclass
from datetime import datetime


@dataclass
class HistoryEntry:
    url: str
    used: int = 0
    last: datetime = datetime.now(tz=None)
