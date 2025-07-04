import re
from dataclasses import dataclass


@dataclass
class Pattern:
    xpath: str | None = None
    regex: re.Pattern | None = None


@dataclass
class ContentPatterns:
    content: list[Pattern]
    content_cleanup: list[Pattern]
    title: list[Pattern]
    date: list[Pattern]
    images: list[Pattern]

    def __init__(self, **kwargs) -> None:
        self.content = [Pattern()]
        self.content_cleanup = [Pattern()]
        self.title = [Pattern()]
        self.date = [Pattern()]
        self.images = [Pattern()]
