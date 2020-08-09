# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import re
from pymongo import MongoClient


class LmparserPipeline:
    def open_spider(self, spider):
        client = MongoClient('localhost', 27017)
        client.lm[spider.search_name].drop()
        self.mongo_collection = client.lm[spider.search_name]

    def process_item(self, item, spider):
        self.mongo_collection.insert_one(item)
        return item


class LmPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    r = scrapy.Request(img)
                    title = item['title']
                    title = re.sub(r'[^\w]+', '_', title)
                    r.meta['title_file_name'] = title
                    yield r
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        p = super().file_path(request, response, info)
        if p is None or p == '':
            return p
        p = p.split('/', 2)
        p = p[0] + '/' + info.spider.search_name + '/' + request.meta['title_file_name'] + '_' + p[1]
        return p

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
