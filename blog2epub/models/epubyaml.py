from dataclasses import dataclass


@dataclass
class EpubYamlChapter:
    title: str
    url: str
    subtitle: str | None = None


@dataclass
class EpubYamlModel:
    title: str
    subtitle: str
    chapters: list[EpubYamlChapter]

    def __init__(self, **kwargs) -> None:
        self.chapters = []
