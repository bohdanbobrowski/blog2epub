from abc import ABC, abstractmethod


class EmptyInterface(ABC):
    """Empty interface for script output."""

    @abstractmethod
    def print(self, **kwargs):
        pass

    @abstractmethod
    def exception(self, **kwargs):
        pass
