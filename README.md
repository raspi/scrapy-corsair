# scrapy-corsair

Web crawler for Corsair ([corsair.com](https://www.corsair.com))

## Requirements

* Python
* [Scrapy](https://scrapy.org/)

## Notes

* 30 day cache is used in `settings.py`

## Spiders

All items are downloaded as JSON in the `items/` directory.

### Memory modules for all motherboards from certain manufacturer

    scrapy crawl manufacturer -a manufacturer="Super Micro"

This will generate `items/Memory/Super Micro/<motherboard model>.json` which then lists all compatible memory modules for this motherboard.

### Memory modules for certain motherboard

    scrapy crawl motherboard -a product="X11SSQ"

This will generate `items/Memory/_unknown/X11SSQ.json` which then lists all compatible memory modules for this motherboard.
Manufacturer directory is `_unknown` because this information is not available.
