from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class BookSynopsisModel(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    urls: List[HttpUrl]


class CommentModel(BaseModel):
    title: Optional[str]
    date: Optional[datetime]
    author: Optional[str]
    content: Optional[str]


class ArticleModel(BaseModel):
    url: HttpUrl
    title: Optional[str]
    subtitle: Optional[str]
    date: Optional[datetime]
    content: Optional[str]
    comments: List[CommentModel]


class BookModel(BaseModel):
    url: HttpUrl
    title: Optional[str]
    subtitle: Optional[str]
    articles: List[ArticleModel]
