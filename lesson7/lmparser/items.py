# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

def process_photos(value):
    if value is None:
        return value
    value = value.replace("_82", '_1200')
    if value[:2] == '//':
        value = f'http:{value}'
    return value

class LmparserItem(scrapy.Item):
    _id = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(process_photos))
    price = scrapy.Field(input_processor=MapCompose(
        lambda s: float(''.join([n for n in s if n.isdigit() or n == '.' or n == ',']) if s is not None else None)),
        output_processor=TakeFirst())
    characteristics = scrapy.Field(output_processor=TakeFirst())



