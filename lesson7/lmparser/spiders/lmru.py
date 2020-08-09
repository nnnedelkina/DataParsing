import scrapy
from scrapy.http import HtmlResponse
from lmparser.items import LmparserItem
from scrapy.loader import ItemLoader
import re


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.search = search
        self.search_name = re.sub(r'[^\w]+', '_', search).lower()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}&plpView=largeCard']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//div[@class='next-paginator-button-wrapper']//a/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        lm_links = response.css('product-card::attr(data-product-url)').extract()
        for link in lm_links:
            yield response.follow(link, callback=self.lm_parse)


    def lm_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LmparserItem(), response=response)
        loader.add_xpath('title', "//h1/text()")
        loader.add_xpath('photos', "//uc-pdp-media-carousel/img[@slot='thumbs']/@src")
        loader.add_xpath('price', "//uc-pdp-price-view[@slot='primary-price']/meta[@itemprop='price']/@content")
        loader.add_value('link', response.url)
        characteristics_divs = response.xpath("//dl[@class='def-list']/div[@class='def-list__group']")
        characteristics = {}
        for x in characteristics_divs:
            k = x.xpath("./dt[@class='def-list__term']/text()").extract_first()
            if k is not None:
                v = x.xpath("./dd[@class='def-list__definition']/text()").extract_first()
                if v is not None:
                    characteristics[k] = re.sub(r'^[\s]+', '', re.sub(r'[\s]+$', '', v))
        loader.add_value('characteristics', characteristics)
        yield loader.load_item()

