from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from pprint import pprint
from pymongo import MongoClient
import re
from datetime import date
import json

# Внимание, код еще дорабатывается, есть ошибка с прокруткой, окончательная версия будет в течение часа

config = { # можно приделать загрузку с json-а
    'link': 'https://www.mvideo.ru/',
    'max_pages': 20
}

def parse_hits_from_mvideo_ru(config):
    driver.maximize_window()
    driver.get(config['link'])

    time.sleep(5)

    hits_dict = {}
    hits_count = 0
    for s in range(config['max_pages']):
        time.sleep(3)
        hits_block = driver.find_elements_by_xpath(
            "//div[contains(text(),'Хиты продаж')]/../../../div[@class='gallery-layout sel-hits-block ']")
        if len(hits_block) == 0:
            break
        time.sleep(1)
        hits_block = hits_block[0]
        items = hits_block.find_elements_by_xpath(".//li[contains(@class, 'gallery-list-item')]//a[contains(@class, 'sel-product-tile-title')]")
        if len(items) == 0:
            break
        for item in items:
            try:
                itemd = {}
                itemd['link'] = item.get_attribute('href')
                itemd['product_info'] = json.loads(item.get_attribute('data-product-info'))
            except:
                continue
            if itemd['link'] not in hits_dict:
                hits_dict[itemd['link']] = itemd
        print(f'Скрол #{s}: получено {len(items)}, стало в словаре {len(hits_dict)}, было в словаре {hits_count}')
        if len(hits_dict) == hits_count:
            break
        hits_count = len(hits_dict)
        next_btn = hits_block.find_elements_by_xpath(".//a[@class='next-btn sel-hits-button-next']")
        if len(next_btn) == 0:
            break
        next_btn[0].click()

    return list(hits_dict.values())


driver = webdriver.Chrome()
hits = parse_hits_from_mvideo_ru(config)
#driver.close()
pprint(hits)

client = MongoClient('127.0.0.1', 27017)
hits_col = client['mvideo_db'].hits
hits_col.drop()
hits_col.insert_many(hits)

hits_from_db = list(hits_col.find())
pprint(hits_from_db)
print(f'Всего {len(hits_from_db)} хитов продаж')

