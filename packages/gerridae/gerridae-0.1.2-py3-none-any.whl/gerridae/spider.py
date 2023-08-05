import requests
from datetime import datetime
from .log import get_logger

logger = get_logger(__name__)


class Spider:
    def __init__(self):
        pass

    start_urls = []
    encoding = None

    def _start(self, url):
        pass

    def parse(self, response):
        raise NotImplementedError

    @classmethod
    def start(cls):
        start_time = datetime.now()
        spider_ins = cls()
        if isinstance(spider_ins.start_urls, list):
            data = []
            for url in cls.start_urls:
                response = requests.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KH"
                        "TML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
                    },
                )
                response.encoding = (
                    spider_ins.encoding if spider_ins is not None else response.encoding
                )
                result = spider_ins.parse(response)
                data.append(result)
        elif isinstance(spider_ins.start_urls, str):
            response = requests.get(
                spider_ins.start_urls,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KH"
                    "TML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
                },
            )
            data = spider_ins.parse(response)
        else:
            raise ValueError("start_urls must be STR or list")

        logger.info(f"total time is {datetime.now() - start_time}")
        return data
