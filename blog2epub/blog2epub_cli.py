import argparse
import platform

from blog2epub import Blog2Epub
from blog2epub.common.book import Book
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.configuration import ConfigurationModel


class CliInterface(EmptyInterface):
    def print(self, text: str, end: str = "\n"):
        print(text, end=end)

    def exception(self, e):
        print(e)


def main():
    parser = argparse.ArgumentParser(
        prog="Blog2epub Cli interface",
        description="Convert blog (blogspot.com, wordpress.com or another based on Wordpress) to epub using CLI or GUI.",
    )
    parser.add_argument("url", help="url of blog to download")
    parser.add_argument("-l", "--limit", type=int, default=None, help="articles limit")
    parser.add_argument("-s", "--skip", type=int, default=None, help="number of skipped articles")
    parser.add_argument("-q", "--quality", type=int, default=40, help="images quality (0-100)")
    parser.add_argument("-o", "--output", help="output path (for cache and epub)", default=".")
    parser.add_argument("-d", "--debug", action="store_true", help="turn on debug")
    args = parser.parse_args()
    configuration = ConfigurationModel(
        url=args.url,
        limit=str(args.limit),
        skip=str(args.skip),
        images_quality=args.quality,
        destination_folder=args.output,
    )
    blog2epub = Blog2Epub(
        url=args.url,
        configuration=configuration,
        cache_folder=args.output,
        interface=CliInterface(),
    )
    configuration.language = blog2epub.crawler.language
    blog2epub.download()
    ebook = Book(
        book_data=blog2epub.crawler.get_book_data(),
        configuration=configuration,
        destination_folder=".",
        interface=CliInterface(),
        platform_name=f"CLI {platform.system()} {platform.release()}",
        debug=args.debug,
    )
    ebook.save(file_name=args.output)


if __name__ == "__main__":
    main()
