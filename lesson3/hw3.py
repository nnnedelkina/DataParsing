from pymongo import MongoClient

from bs4 import BeautifulSoup as bs
import requests
from sys import argv
import re

######################################################################
# Доработанные фукнции из предыдущего задания

#_________________________________________________________________
def parse_number(s):
    s = ''.join([n for n in s if n.isdigit()])
    return 0 if s == '' else int(s)

#_________________________________________________________________
# Для определения уникальности выделяем id из ссылки
def parse_id_from_link(s):
    r = re.search(r'([1-9]\d{4,})', s)
    return int(r.group(1) if r is not None else 0)


#_________________________________________________________________
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
            break  # если нет такой страницы или другая ошибка, не обрабатываю другие ситуации
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
                    res['id'] = parse_id_from_link(res['link'])
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
    return result

#_________________________________________________________________
def get_superjob(search_text, max_pages=1000):
    result = []
    for page in range(1, max_pages + 1):
        response = requests.get(superjob_link,
                                params={'keywords': search_text, 'page': page},
                                headers={"User-Agent": user_agent},
                                cookies={"geo": "", "geoSet": "0"})
        if response.status_code != 200:
            break  # если нет такой страницы или другая ошибка, не обрабатываю другие ситуации
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
                res['id'] = 10**15 + parse_id_from_link(res['link'])
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
    return result

#_________________________________________________________________
def load_vacancies(search_text, max_pages):
    all = None
    if site_filter is None or site_filter[0:2] == 'hh':
        print("Получаем вакансии с hh.ru")
        all = get_hh(search_text, max_pages)


    if site_filter is None or site_filter[0:2] == 'su':
        print("Получаем вакансии с superjob.ru")
        sj = get_superjob(search_text, max_pages)
        all = sj if all is None else all + sj
    return all

######################################################################
## Функции для работы с MongoDB
######################################################################

#_________________________________________________________________
def add_all(col, docs):
    col.drop()
    col.insert_many(docs)

#_________________________________________________________________
def find_vacancies(col, compensation, is_max):
    # валюта не учитывается! работайте за рубли!
    for vac in col.find({'max_compensation' if is_max else 'min_compensation': {'$gt': compensation}}):
        print(vac)

#_________________________________________________________________
def add_if_new(vacancies, docs):
    added = 0
    for d in docs:
        r = vacancies.find({'id': d['id']}) # Для определения уникальности выделяем id из ссылки
        if r is None or r.count() == 0:
            vacancies.insert_one(d)
            added += 1
    print(f'добавлено: {added} вакансий')




#########################################################################
if len(argv) < 2:
    print(f'использование: {argv[0]} <ключевые слова для поиска> [<максимальное число страниц> [<сайт для поиска>]]')
    exit(1)

search_text = argv[1]

max_pages = 1
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


client = MongoClient('127.0.0.1', 27017)
vacancies = client['vacancies_db'].vacancies

print(f'Загружаем {max_pages} страниц вакансий')
all = load_vacancies(search_text, max_pages)
print(f'Добавляем {len(all)} найденных вакансий')
add_all(vacancies, all)
print(f'Всего в коллекции {vacancies.count_documents({})} вакансий')

print(f'Загружаем {max_pages + 1} страниц вакансий')
all = load_vacancies(search_text, max_pages + 1)
print(f'Добавляем {len(all)} найденных вакансий, только новые')
add_if_new(vacancies, all)
print(f'Всего в коллекции {vacancies.count_documents({})} вакансий')

while True:
    try:
        c = int(input('Введите зарплату для поиска или любое не-число для выхода: '))
        is_max = bool(input('Проверять максимальную запрлату (непусто - да, enter - нет)? '))
    except:
        break
    find_vacancies(vacancies, c, is_max)



