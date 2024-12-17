import re

from pydantic import BaseModel


class Pattern(BaseModel):
    xpath: str | None = None
    regex: re.Pattern | None = None


class ContentPatterns(BaseModel):
    content: list[Pattern] = [Pattern()]
    content_cleanup: list[Pattern] = [Pattern()]
    title: list[Pattern] = [Pattern()]
    date: list[Pattern] = [Pattern()]
    images: list[Pattern] = [Pattern()]
