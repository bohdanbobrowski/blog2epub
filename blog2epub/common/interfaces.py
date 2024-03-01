from abc import ABC, abstractmethod


class EmptyInterface(ABC):
    """Empty interface for script output."""

    @abstractmethod
    def print(self, text):
        pass

    @abstractmethod
    def exception(self, e):
        pass
