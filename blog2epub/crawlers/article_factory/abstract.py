from abc import ABC, abstractmethod


class AbstractArticleFactory(ABC):
    @abstractmethod
    def process(self):
        pass
