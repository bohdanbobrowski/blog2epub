from datetime import datetime
from typing import Optional

from blog2epub.common.globals import VERSION
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.configuration import ConfigurationModel
from blog2epub.crawlers import (
    AbstractCrawler,
    BlogspotCrawler,
    DefaultCrawler,
    WordpressCrawler,
    NrdblogCmosEuCrawler,
    ZeissIkonVEBCrawler,
)


class Blog2Epub:
    """Main Blog2Epub class."""

    version = VERSION
    crawler: AbstractCrawler

    def __init__(
        self,
        url: str,
        configuration: ConfigurationModel,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        file_name: Optional[str] = None,
        cache_folder: str = "",
        interface: EmptyInterface = EmptyInterface(),
    ):
        # TODO: Refactor this!
        crawler_args = {
            "url": url,
            "configuration": configuration,
            "start": start,
            "end": end,
            "file_name": file_name,
            "cache_folder": cache_folder,
            "interface": interface,
        }

        self.crawler = DefaultCrawler(**crawler_args)  # type: ignore
        if url.find(".blogspot.") > -1:
            self.crawler = BlogspotCrawler(**crawler_args)
        if url.find(".wordpress.com") > -1:
            self.crawler = WordpressCrawler(**crawler_args)
        if url.find("nrdblog.cmosnet.eu") > -1:
            self.crawler = NrdblogCmosEuCrawler(**crawler_args)  # type: ignore
        if url.find("zeissikonveb.de") > -1:
            self.crawler = ZeissIkonVEBCrawler(**crawler_args)  # type: ignore

    def download(self):
        self.crawler.crawl()
