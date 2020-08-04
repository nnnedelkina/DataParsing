from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from pprint import pprint
from pymongo import MongoClient
import re
from datetime import date



config = { # можно приделать загрузку с json-а
    'link': 'https://account.mail.ru/login',
    'username': 'study.ai_172',
    'password': 'NextPassword172',
    'max_pages': 20,
}

def parse_mail_ru(config):
    driver.get(config['link'])

    time.sleep(2)

    username = driver.find_element_by_xpath("//input[@name='username']")
    username.send_keys(config['username'])
    password = driver.find_element_by_xpath("//button[@data-test-id='next-button']")
    password.click()
    time.sleep(2)
    password = driver.find_element_by_xpath("//input[@name='password']")
    password.send_keys(config['password'])
    login = driver.find_element_by_xpath("//button[@data-test-id='submit-button']")
    login.click()
    time.sleep(5)

    emails_dict = {}
    emails_count = 0
    for s in range(config['max_pages']):
        time.sleep(2)
        items = driver.find_elements_by_xpath("//div[contains(@class, 'dataset__items')]//a[contains(@class, 'llc')]")
        if len(items) == 0:
            return []
        for item in items:
            try:
                itemd = {}
                itemd['link'] = item.get_attribute('href')
                itemd['sender'] = item.find_element_by_css_selector("span.ll-crpt").get_attribute('title')
                itemd['subject'] = item.find_element_by_css_selector("span.ll-sj__normal").text
                itemd['date'] = item.find_element_by_css_selector("div.llc__item_date").get_attribute('title')
            except:
                continue
            emails_dict[itemd['link']] = itemd
        print(f'Скрол #{s}: получено {len(items)}, стало в словаре {len(emails_dict)}, было в словаре {emails_count}')
        if len(emails_dict) == emails_count:
            break
        emails_count = len(emails_dict)
        ActionChains(driver).move_to_element(items[-1]).perform()

    print('Получаем тела сообщений')
    for itemd in emails_dict.values():
        try:
            driver.get(itemd['link'])
            time.sleep(2)
            itemd['body_text'] = driver.find_element_by_css_selector('div.letter-body__body-content').text
            itemd['body_html'] = driver.find_element_by_css_selector('div.letter-body__body-content').get_attribute('innerHTML')
        except:
            continue

    return list(emails_dict.values())


driver = webdriver.Chrome()
emails = parse_mail_ru(config)
driver.close()

client = MongoClient('127.0.0.1', 27017)
emails_col = client['email_db'].emails
emails_col.drop()
emails_col.insert_many(emails)

emails_from_db = list(emails_col.find())
pprint(emails_from_db)
print(f'Всего {len(emails_from_db)} писем')

