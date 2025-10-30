import re
from dataclasses import dataclass, field


@dataclass
class Pattern:
    xpath: str | None = None
    regex: re.Pattern | None = None


@dataclass
class ContentPatterns:
    content: list[Pattern] = field(default_factory=list)
    content_cleanup: list[Pattern] = field(default_factory=list)
    title: list[Pattern] = field(default_factory=list)
    date: list[Pattern] = field(default_factory=list)
    images: list[Pattern] = field(default_factory=list)
