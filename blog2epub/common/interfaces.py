import sys


class EmptyInterface:
    """Empty interface for script output."""

    def delete_line(self):
        sys.stdout.write("\033[K")

    def print(self, text: str, end: str = "\n"):
        print(text, end=end)

    def exception(self, **kwargs):
        print(kwargs)
