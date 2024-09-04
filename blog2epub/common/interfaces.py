class EmptyInterface:
    """Empty interface for script output."""

    def print(self, text: str):
        print(text)

    def exception(self, **kwargs):
        print(kwargs)
