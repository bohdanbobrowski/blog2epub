import argparse

from blog2epub.common.interfaces import EmptyInterface


class CliInterface(EmptyInterface):
    def print(self, text: str):
        print(text)

    def exception(self, e):
        print(e)


def main():
    parser = argparse.ArgumentParser(
        prog="Blog2epub Cli interface",
        description="Convert blog (blogspot.com, wordpress.com or another based on Wordpress) to epub using CLI or GUI.",
    )
    parser.add_argument("url", help="url of blog to download")
    parser.add_argument("-l", "--limit", type=int, default=None, help="articles limit")
    parser.add_argument("-s", "--skipped", type=int, default=None, help="number of skipped articles")
    parser.add_argument("-o", "--output", help="output epub file name")
    parser.add_argument("-d", "--debug", action="store_true", help="turn on debug")
    args = parser.parse_args()

    print(args)

    # blog2epub = Blog2Epub()
    # blog2epub.download()
    # book_data = blog2epub.crawler.get_book_data()
    # ebook = Book(
    #     book_data=book_data,
    #     configuration=ConfigurationModel(
    #         language=blog2epub.crawler.language,
    #     ),
    #     interface=params["interface"],
    #     destination_folder=str("."),
    # )
    # ebook.save(book_data.articles)


if __name__ == "__main__":
    main()
