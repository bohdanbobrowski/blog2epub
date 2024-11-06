import re
from typing import Optional

from pydantic import BaseModel


class PatternElement(BaseModel):
    xpath: Optional[str] = None
    regex: Optional[re.Pattern] = None


class ContentPatterns(BaseModel):
    content: list[PatternElement]
    content_cleanup: list[PatternElement]
    title: list[PatternElement]
    images: list[PatternElement]
