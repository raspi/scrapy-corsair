import json
import os
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile

from corsair.items import *


class CorsairPipeline:
    def process_item(self, item, spider):
        basepath = os.path.abspath(os.path.join("..", "items"))
        fullpath = None

        if isinstance(item, Memory):
            fname = item['_model'] + ".json"
            basepath = os.path.abspath(os.path.join(basepath, "Memory", item['_manufacturer']))
            fullpath = os.path.abspath(os.path.join(basepath, fname))

            module = item['memory']
            del item['memory']

            modulename = module['code']
            del module['code']

            item['modules'] = {
                modulename: module,
            }

            if os.path.isfile(fullpath):
                with open(fullpath, "r", encoding='utf8') as f:
                    olditem = json.loads(f.read())
                    item['modules'].update(olditem['modules'])

        if fullpath is not None:
            if not isinstance(item, dict):
                return

            Path(basepath).mkdir(parents=True, exist_ok=True)

            # Save to temporary file
            tmpf = NamedTemporaryFile("w", prefix="kingston-item-", suffix=".json", encoding="utf8", delete=False)
            with tmpf as f:
                json.dump(item, f)
                f.flush()
                spider.logger.info(f"saved as {f.name}")

            # Rename and move the temporary file to actual file
            newpath = move(tmpf.name, fullpath)
            spider.logger.info(f"renamed {tmpf.name} to {newpath}")
