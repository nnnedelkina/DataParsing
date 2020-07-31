from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient
import re
from datetime import date

#=============================================================================
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
mail_link = 'https://news.mail.ru'
lenta_link = 'https://lenta.ru'
yandex_link = 'https://news.yandex.ru'
today = date.today()

#_____________________________________________________________________________
def get_mail_ru(section):

    def parse_mail_article(d):
        news_response = requests.get(d['link'], headers=header)
        news_dom = html.fromstring(news_response.text)
        news_date = news_dom.xpath("//div[@class='article js-article js-module']//span[@datetime]")
        if len(news_date) > 0:
            d['date'] = news_date[0].get('datetime')
        news_source = news_dom.xpath("//div[@class='article js-article js-module']//a/span/text()")
        if len(news_source) > 0:
            d['source'] = news_source[0]


    response = requests.get(mail_link, headers=header)
    if not response.ok:
        return []
    dom = html.fromstring(response.text)

    news = []
    news_div = dom.xpath('//a[@class="hdr__text"  and contains(@href, "/' + section + '/")]/../../..')
    if len(news_div) == 0:
        return news
    news_div = news_div[0]

    news_links = news_div.xpath(".//a[@class='newsitem__title link-holder']") \
        + news_div.xpath(".//a[@class='link link_flex']")

    for item in news_links:
        news_item = {
            'link': item.get('href'),
            'title': item.xpath("./span/text()")[0]
        }
        parse_mail_article(news_item)
        news.append(news_item)

    return news

#_____________________________________________________________________________
def get_lenta_ru():
    response = requests.get(lenta_link, headers=header)
    if not response.ok:
        return []
    dom = html.fromstring(response.text)

    news = []
    news_links = dom.xpath("//section[contains(@class, 'js-top-seven')]//div[contains(@class, 'span4')]//div[contains(@class, 'item')]//a[time]")
    for item in news_links:
        news_item = {
            'link': item.get('href'),
            'title': re.sub(r'\s', ' ', item.xpath("./text()")[0]),
            'date': item.xpath("./time")[0].get('datetime')
        }
        if news_item['link'].startswith('/'):
            news_item['link'] = lenta_link + news_item['link']
            news_item['source'] = 'lenta.ru'
        else:
            site = re.match(r'https*://([\w\.]+)/', news_item['link'])
            if site is not None:
                news_item['source'] = site.group(1)
        news.append(news_item)

    return news

#_____________________________________________________________________________
def get_yandex_ru(section):
    response = requests.get(yandex_link, headers=header)
    if not response.ok:
        return []
    dom = html.fromstring(response.text)
#    print(dom)
    news = []

    news_links = dom.xpath("//a[contains(@class, 'rubric-label') and contains(@href, '/" + section + "')]/ancestor::div[contains(@class, 'stories-set')]//*[@class='stories-set__item']")
    for item in news_links:
        news_a = item.xpath(".//*[@class='story__title']//a")
        if len(news_a) == 0:
            continue
        news_a = news_a[0]
        news_item = {
            'link': yandex_link + news_a.get('href'),
            'title': news_a.text
        }
        news_info = item.xpath(".//*[@class='story__date']/text()")
        if len(news_info) == 0:
            continue
        news_info = news_info[0]
        news_info_parsed = re.search(r'(.+)\s+(\d+\:\d+)', news_info)
        if re is not None:
            news_item['source'] = news_info_parsed.group(1)
            news_item['date'] = today.strftime("%Y-%b-%d") + ' ' + news_info_parsed.group(2)
        news.append(news_item)

    return news



#========================================================================================
news = []
news += get_mail_ru('politics')
news += get_lenta_ru()
news += get_yandex_ru('politics')


client = MongoClient('127.0.0.1', 27017)
news_col = client['news_db'].news
news_col.drop()
news_col.insert_many(news)

pprint(list(news_col.find()))
