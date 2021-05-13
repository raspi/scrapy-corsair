import json
import os
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile
from typing import List

import scrapy

from corsair.items import *


class CorsairPipeline:
    items: List[Memory] = []

    def process_item(self, item: Item, spider: scrapy.Spider):
        if not isinstance(item, Item):
            spider.log("invalid item type {0}".format(type(item)))
            return

        if isinstance(item, Memory):
            self.items.append(item)

    def close_spider(self, spider: scrapy.Spider):
        basepath = os.path.abspath(os.path.join("..", "items", "Memory"))
        fullpath = None

        components: dict = {
        }

        for item in self.items:
            if item['_manufacturer'] not in components:
                components[item['_manufacturer']]: dict = {}

            if item['_model'] not in components[item['_manufacturer']]:
                components[item['_manufacturer']][item['_model']]: dict = {
                    "_manufacturer": item['_manufacturer'],
                    "_model": item['_model'],
                    "modules": {},
                }

            module = item['memory']
            del item['memory']

            modulename = module['code']
            del module['code']

            if modulename not in components[item['_manufacturer']][item['_model']]['modules']:
                components[item['_manufacturer']][item['_model']]['modules'][modulename] = module

        for manufacturer in components:
            for model in components[manufacturer]:
                Path(os.path.join(basepath, manufacturer)).mkdir(parents=True, exist_ok=True)
                fullpath = os.path.abspath(os.path.join(basepath, manufacturer, model)) + ".json"

                # Save to temporary file
                tmpf = NamedTemporaryFile("w", prefix="corsair-item-", suffix=".json", encoding="utf8", delete=False)
                with tmpf as f:
                    json.dump(components[manufacturer][model], f)
                    f.flush()
                    spider.logger.info(f"saved as {f.name}")

                # Rename and move the temporary file to actual file
                newpath = move(tmpf.name, fullpath)
                spider.logger.info(f"renamed {tmpf.name} to {newpath}")
