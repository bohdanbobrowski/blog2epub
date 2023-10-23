import sys
from urllib import parse

from blog2epub.Blog2Epub import BadUrlException, Blog2Epub, NotEnoughCommandsException
from blog2epub.crawlers.Crawler import EmptyInterface


class CliInterface(EmptyInterface):
    @staticmethod
    def print(text):
        print(text)

    @staticmethod
    def exception(e):
        print(e)


class Blog2EpubCli:
    """Command line interface for Blog2Epub class."""

    def __init__(self, defaults={}):
        params = {**defaults, **self.parse_parameters()}
        blog2epub = Blog2Epub(params)
        blog2epub.download()

    @staticmethod
    def get_url():
        if len(sys.argv) > 1:
            if parse.urlparse(sys.argv[1]):
                return sys.argv[1]
            raise BadUrlException("Blog url is not valid.")
        raise NotEnoughCommandsException("Not enough command line parameters.")

    def parse_parameters(self):
        params = {"interface": CliInterface()}
        try:
            params["url"] = self.get_url()
        except BadUrlException or NotEnoughCommandsException as e:
            print(e)
            print("usage: blog2epub <blog_name> [params...]")
            exit()

        params["url"] = sys.argv[1]

        if "-n" in sys.argv or "--no-images" in sys.argv:
            params["include_images"] = False
        for arg in sys.argv:
            if arg.find("-l=") == 0:
                params["limit"] = int(arg.replace("-l=", ""))
            if arg.find("--limit=") == 0:
                params["limit"] = int(arg.replace("--limit=", ""))
            if arg.find("-s=") == 0:
                params["skip"] = int(arg.replace("-s=", ""))
            if arg.find("--skip=") == 0:
                params["skip"] = int(arg.replace("--skip=", ""))
            if arg.find("-q=") == 0:
                params["images_quality"] = int(arg.replace("-q=", ""))
            if arg.find("--quality=") == 0:
                params["images_quality"] = int(arg.replace("--quality=", ""))
        return params


def main():
    Blog2EpubCli()


if __name__ == "__main__":
    main()
