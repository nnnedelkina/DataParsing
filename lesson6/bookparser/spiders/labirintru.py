import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5%20python/?stype=0']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[contains(@class,'pagination-next__text')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        book_links = response.css('a.cover::attr(href)').extract()
        for link in book_links:
            yield response.follow(link,callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        title = response.xpath("//div[@id='product-info']/@data-name").extract_first()
        authors = response.xpath("//div[@class='authors'][1]/a/text()").extract()
        price = response.xpath("//span[@class='buying-priceold-val-number']/text()").extract_first()
        discount_price = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract_first()
        rate = response.xpath("//div[@id='rate']/text()").extract_first()
        yield BookparserItem(link=link, title=title, authors=authors, price=price, discount_price=discount_price, rate=rate)
