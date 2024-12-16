
from pydantic import BaseModel


class EpubYamlChapter(BaseModel):
    title: str
    subtitle: str | None = None
    url: str


class EpubYamlModel(BaseModel):
    title: str
    subtitle: str
    chapters: list[EpubYamlChapter] = []
