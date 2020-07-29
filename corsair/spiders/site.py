import json
from urllib.parse import urlsplit, urlencode, unquote, urljoin
from urllib.parse import parse_qsl as queryparse

import scrapy

from corsair.items import *


class BaseSpider(scrapy.Spider):
    allowed_domains = [
        'corsair.com',
        'www.corsair.com',
    ]

    manufacturer = None
    memmodules = []

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError

    def parse_motherboard(self, response: scrapy.http.Response):
        query = dict(queryparse(urlsplit(response.url).query))
        current_page = int(query['page'])

        data = json.loads(response.body)
        for memmodule in data['results']:

            if 'url' in memmodule:
                memmodule['url'] = response.urljoin(memmodule['url'])

            remove_keys = [
                'stock',
                'priceRange',
                'availableForPickup',
            ]

            for idx, (k, v) in enumerate(memmodule.items()):
                if v is None:
                    remove_keys.append(k)

            for k in remove_keys:
                if k in memmodule:
                    del memmodule[k]

            if 'stock' in memmodule:
                del memmodule['stock']

            yield Memory({
                '_manufacturer': self.manufacturer,
                '_model': response.meta['model'],
                'memory': memmodule,
            })

        if current_page == 0 and data['pagination']['numberOfPages'] > 1:
            for pnum in range(1, data['pagination']['numberOfPages']):
                query['page'] = str(pnum)

                # Call the same page with increased page number
                yield scrapy.Request(
                    response.urljoin("?" + urlencode(query)),
                    callback=self.parse_motherboard,
                    meta={
                        'model': response.meta['model'],
                    },
                )


class ManufacturerSpider(BaseSpider):
    name = 'manufacturer'

    start_urls = [
        'https://www.corsair.com/us/en/memoryfinder/searchMotherboard/',
    ]

    def __init__(self, manufacturer: str = ""):
        if manufacturer == "":
            manufacturer = None

        if manufacturer is None:
            raise ValueError("Invalid product given")

        self.manufacturer = manufacturer

        self.start_urls = [
            f'https://www.corsair.com/us/en/memoryfinder/searchMotherboard/{manufacturer}',
        ]

    def parse(self, response: scrapy.http.Response):
        """
        Get manufacturer's list of motherboards
        """

        for x in json.loads(response.body):
            fquery = f'motherboards_sortabletext_mv:"{x["code"]}"'
            fquery += ' AND productBackendStatus_boolean:true'
            # 'numMemoryCapacity_int:[2 TO 128] AND '\
            fquery += ' AND numMemoryModule_int:[1 TO 1]'

            query = {
                'q': ':price-desc:',
                'rawFilterQuery': '(' + fquery + ')',
                'page': '0',
                'sort': 'price-asc',
            }

            yield scrapy.Request(
                'https://www.corsair.com/us/en/c/Cor_Products_Memory/results?' + urlencode(query),
                callback=self.parse_motherboard,
                meta={
                    'model': x['code'],
                },
            )


class MotherboardSpider(BaseSpider):
    """
    Get compatible memory modules for given motherboard
    """
    name = 'motherboard'

    start_urls = [
        'https://www.corsair.com/us/en/memoryfinder/searchMotherboard/',
    ]

    product = None

    def __init__(self, product: str = ""):
        if product == "":
            product = None

        if product is None:
            raise ValueError("Invalid product given")

        self.product = product

        self.manufacturer = "_unknown"

        fquery = f'motherboards_sortabletext_mv:"{self.product}"'
        fquery += ' AND productBackendStatus_boolean:true'
        # 'numMemoryCapacity_int:[2 TO 128] AND '\
        fquery += ' AND numMemoryModule_int:[1 TO 1]'

        query = {
            'q': ':price-desc:',
            'rawFilterQuery': '(' + fquery + ')',
            'page': '0',
            'sort': 'price-asc',
        }

        self.start_urls = [
            'https://www.corsair.com/us/en/c/Cor_Products_Memory/results?' + urlencode(query),
        ]

    def parse(self, response: scrapy.http.Response):
        yield scrapy.Request(
            response.url,
            callback=self.parse_motherboard,
            meta={
                'model': self.product,
            },
        )
