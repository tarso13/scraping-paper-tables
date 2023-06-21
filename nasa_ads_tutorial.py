from password import get_password
import requests
from urllib.parse import urlencode

token=get_password('nasa_ads_token.txt')

encoded_query = urlencode({"q": "'aanda'",
                           "fq": "year:[2018 TO 2023]",
                           "fl": "title",
                           "rows": 100
                          })

results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query), \
                       headers={'Authorization': 'Bearer ' + token})

print(results.json())