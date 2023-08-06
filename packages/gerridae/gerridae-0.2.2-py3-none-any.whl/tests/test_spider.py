"""
test the integer field
"""
import asyncio

from gerridae import Item, Spider, TextField
from gerridae.log import get_logger

logger = get_logger(__name__)


class GerridaeItem(Item):
    command = TextField(css_select="#pip-command")


class GerridaeSpider(Spider):
    start_urls = "https://pypi.org/project/gerridae/"

    async def parse(self, resp):
        text = await resp.text(encoding='utf-8')
        result = GerridaeItem.get_item(html=text)
        return result


def test_spider():
    results = asyncio.run(GerridaeSpider.start())
    assert "pip install gerridae" == results[0].command
