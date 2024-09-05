from datetime import datetime
from typing import Optional

from blog2epub.common.globals import VERSION
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.configuration import ConfigurationModel


class Blog2Epub:
    """Main Blog2Epub class."""

    version = VERSION

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
        crawler_class_name = self._get_crawler_class_name(url)
        self.crawler = eval(crawler_class_name)(
            url=url,
            configuration=configuration,
            start=start,
            end=end,
            file_name=file_name,
            cache_folder=cache_folder,
            interface=interface,
        )

    def _get_crawler_class_name(self, url: str) -> str:
        if url.find(".blogspot.") > -1:
            return "BlogspotCrawler"
        if url.find(".wordpress.com") > -1:
            return "WordpressCrawler"
        if url.find("nrdblog.cmosnet.eu") > -1:
            return "NrdblogCmosEuCrawler"
        if url.find("zeissikonveb.de") > -1:
            return "ZeissIkonVEBCrawler"
        return "UniversalCrawler"

    def download(self):
        self.crawler.crawl()
