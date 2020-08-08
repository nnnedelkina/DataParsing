# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


def parse_number(s):
    return ''.join([n for n in s if n.isdigit()]) if s is not None else None


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        for c in ['labirintru', 'book24ru']:
            client.books[c].drop()
        self.mongo_base = client.books

    def process_item(self, item, spider):
        if item['price'] is None:
            item['price'], item['discount_price'] = item['discount_price'], None
        item['price'] = parse_number(item['price'])
        item['discount_price'] = parse_number(item['discount_price'])

        self.mongo_base[spider.name].insert_one(item)

        return item
