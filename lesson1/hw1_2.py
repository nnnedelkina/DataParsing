import requests
import json
from pprint import pprint
from sys import argv


def print_dataset(ds):
    print(f"{ds['ref']} ({ds['subtitle']})")


if len(argv) < 2:
    print(f'использование: {argv[0]} <имя json-файла формата {{"username":"...","key":"..."}}>')
    exit(1)

key_path = argv[1]
with open(key_path) as f:
    key_json = json.load(f)


main_link = f"https://{key_json['username']}:{key_json['key']}@www.kaggle.com/api/v1/datasets/list"

all_data = []
for p in range(1, 1000):
    print(f"------ page = {p} ---------------------------")
    response = requests.get(main_link, params={'page': p})
    if response.status_code != 200:
        break # просто закончим, не будем пытаться повторно
    data = response.json()
    if len(data) == 0:
        break
    all_data += data
    for d in data:
        print_dataset(d)


with open('../../datasets.json', 'w') as f:
    json.dump(all_data, f, indent=4)



