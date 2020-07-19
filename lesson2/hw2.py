from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
from sys import argv
import re
import pandas as pd

def parse_number(s):
    return ''.join([n for n in s if n.isdigit()])


def get_hh(search_text, max_pages=10000):
    result = []
    for page in range(0, max_pages):
        response = requests.get(hh_link, params={'text': search_text, 'page': page}, headers={"User-Agent": user_agent})
        if response.status_code != 200:
            break  # если нет такой страницы или другая ошибка
        print("анализируем страницу ", page)
        soup = bs(response.text, 'lxml')
        vacancy_divs = soup.find_all('div', {'class': 'vacancy-serp-item'})
        if len(vacancy_divs) == 0:
            break   # если нет такой страницы или другая ошибка
        for v in vacancy_divs:
            res = {}
            ns = v.find('span', {'class': 'resume-search-item__name'})
            if ns is not None:
                a = ns.find('a')
                if a is not None:
    #                print(f'{a.text} href={a.attrs["href"]}')
                    res['source'] = 'hh'
                    res['name'] = a.text
                    res['link'] = a.attrs['href']
                    cs = v.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                    if cs is not None:
     #                   print(cs.text)
                        r = re.search(r'(от|до)?\s*([\d\s]+)(-?)([\d\s]+)\s*([\w$\s\.]*)', cs.text)
                        if r is not None:
                            res['compensation_currency'] = r.group(5)
                            if r.group(1) == 'от':
                                res['min_compensation'] = parse_number(r.group(2))
                            elif r.group(1) == 'до':
                                res['max_compensation'] = parse_number(r.group(2))
                            elif r.group(3) == '-':
                                res['min_compensation'] = parse_number(r.group(2))
                                res['max_compensation'] = parse_number(r.group(4))
                    cs = v.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
                    if cs is not None:
                        res['location'] = cs.text
                    result.append(res)

#    pprint(vacancy_divs[0])
    return pd.DataFrame(result)


def get_superjob(search_text, max_pages=1000):
    result = []
    for page in range(1, max_pages + 1):
        response = requests.get(superjob_link,
                                params={'keywords': search_text, 'page': page},
                                headers={"User-Agent": user_agent},
                                cookies={"geo": "", "geoSet": "0"})
        if response.status_code != 200:
            break  # если нет такой страницы или другая ошибка
        print("анализируем страницу ", page)
        soup = bs(response.text, 'lxml')
        vacancy_divs = soup.find_all('div', {'class': 'f-test-vacancy-item'})
        if len(vacancy_divs) == 0:
            break   # если нет такой страницы или другая ошибка

        for v in vacancy_divs:
            res = {}
            a = v.find('a')
            if a is not None:
    #           print(f'{a.text} href={a.attrs["href"]}')
                res['source'] = 'superjob'
                res['name'] = a.text
                res['link'] = superjob_base_link + a.attrs['href']
                cs = v.find('span', {'class': 'f-test-text-company-item-salary'})
                if cs is not None:
                    cs = cs.find('span')
                    if cs is not None:
#                        print(cs.text)
                        r = re.search(r'(от|до)?\s*([\d\s]+)(-?)([\d\s]+)\s*([\w$\s\.]*)', cs.text)
                        if r is not None:
                            res['compensation_currency'] = r.group(5)
                            if r.group(1) == 'от':
                                res['min_compensation'] = parse_number(r.group(2))
                            elif r.group(1) == 'до':
                                res['max_compensation'] = parse_number(r.group(2))
                            elif r.group(3) == '-':
                                res['min_compensation'] = parse_number(r.group(2))
                                res['max_compensation'] = parse_number(r.group(4))
                cs = v.find('span', {'class': 'f-test-text-company-item-location'})
                if cs is not None:
                    cs = cs.find_all('span')
                    if cs is not None and len(cs) > 2:
                        res['location'] = cs[2].text
                result.append(res)
    return pd.DataFrame(result)



if len(argv) < 2:
    print(f'использование: {argv[0]} <ключевые слова для поиска> [<максимальное число страниц> [<сайт для поиска>]]')
    exit(1)

search_text = argv[1]

max_pages = 10000
if len(argv) > 2:
    max_pages = int(argv[2])

site_filter = None
if len(argv) > 3:
    site_filter = argv[3]


user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'

hh_base_link = 'https://www.hh.ru'
hh_link = hh_base_link + '/search/vacancy'

superjob_base_link = 'https://www.superjob.ru'
superjob_link = superjob_base_link + '/vacancy/search/'

all = None
if site_filter is None or site_filter[0:2] == 'hh':
    print("Получаем вакансии с hh.ru")
    all = get_hh(search_text, max_pages)


if site_filter is None or site_filter[0:2] == 'su':
    print("Получаем вакансии с superjob.ru")
    sj = get_superjob(search_text, max_pages)
    all = sj if all is None else pd.concat((all, sj))

print("Общий результат")
print(all.to_string())
