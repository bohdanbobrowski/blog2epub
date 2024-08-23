from typing import List, Optional
from pydantic import BaseModel
from pydantic_yaml import to_yaml_str


class EpubYamlChapter(BaseModel):
    title: str
    subtitle: Optional[str] = None
    url: str


class EpubYamlModel(BaseModel):
    title: str
    subtitle: str
    cover: Optional[str] = None
    chapters: List[EpubYamlChapter] = []


if __name__ == "__main__":
    bf = EpubYamlModel(
        title="test ebook",
        subtitle="test ebook",
    )
    for x in range(0, 5):
        bf.chapters.append(
            EpubYamlChapter(
                title=f"test chapter {x}",
                url=f"http://example.com/chapter_{x}.html",
            )
        )
    print(to_yaml_str(bf))
