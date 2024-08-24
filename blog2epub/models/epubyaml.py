from typing import List, Optional
from pydantic import BaseModel


class EpubYamlChapter(BaseModel):
    title: str
    subtitle: Optional[str] = None
    url: str


class EpubYamlModel(BaseModel):
    title: str
    subtitle: str
    chapters: List[EpubYamlChapter] = []
