import requests
import json
from pprint import pprint

user = "nnnedelkina"
main_link = f'https://api.github.com/users/{user}/repos'
response = requests.get(main_link)
data = response.json()
##pprint(data)

for r in data:
    print(r['full_name'])

with open('../../repositories.json', 'w') as f:
    json.dump(data, f, indent=4)
