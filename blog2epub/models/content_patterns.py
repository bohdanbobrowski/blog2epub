import re
from typing import Optional

from pydantic import BaseModel


class Pattern(BaseModel):
    xpath: Optional[str] = None
    regex: Optional[re.Pattern] = None


class ContentPatterns(BaseModel):
    content: list[Pattern] = [Pattern()]
    content_cleanup: list[Pattern] = [Pattern()]
    title: list[Pattern] = [Pattern()]
    date: list[Pattern] = [Pattern()]
    images: list[Pattern] = [Pattern()]
