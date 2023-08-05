"""
test the integer field
"""

from gerridae import Item, TextField, Spider
from gerridae.log import get_logger

logger = get_logger(__name__)


class GerridaeItem(Item):
    command = TextField(css_select="#pip-command")


class GerridaeSpider(Spider):
    start_urls = "https://pypi.org/project/gerridae/"

    def parse(self, response):
        result = GerridaeItem.get_item(html=response.text)
        return result


def test_spider():
    result = GerridaeSpider.start()
    assert "pip install gerridae" == result.command


def test_spider_encoding_is_none():
    class GerridaeSpider2(GerridaeSpider):
        encoding = None

        def parse(self, response):
            return response.encoding

    result = GerridaeSpider2.start()
    assert result is None


def test_spider_encoding_is_gbk():
    class GerridaeSpider3(GerridaeSpider):
        encoding = "gbk"

        def parse(self, response):
            return response.encoding

    result = GerridaeSpider3.start()
    assert result == "gbk"
