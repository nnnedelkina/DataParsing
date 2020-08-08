import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[text()='Далее']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        book_links = response.css('a.book__image-link::attr(href)').extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        title = response.xpath("//h1[@class='item-detail__title']/text()").extract_first()
        authors = response.xpath("//span[@class='item-tab__chars-key' and text()='Автор:']/..//a/text()").extract()
        price = response.xpath("//div[@class='item-actions__price-old']/text()").extract_first()
        discount_price = response.xpath("//div[@class='item-actions__price']/b/text()").extract_first()
        rate = response.xpath("//span[@class='rating__rate-value']/text()").extract_first()
        yield BookparserItem(link=link, title=title, authors=authors, price=price, discount_price=discount_price,
                             rate=rate)

