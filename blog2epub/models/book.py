from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class BookSynopsis(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    urls: List[HttpUrl]


class ArticleModel(BaseModel):
    pass


class BookModel(BaseModel):
    pass
