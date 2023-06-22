from password import get_password
import requests
from urllib.parse import urlencode

# get token for nasa api
token=get_password('nasa_ads_token.txt')

# Encode query 
# In this case: search for aanda in publications,
# filter the results for specific period of time,
# title is the return value of the record,
# and retrieve only the first 100 results
encoded_query = urlencode({"q": "'aanda'",
                           "fq": "year:[2018 TO 2023]",
                           "fl": "title",
                           "rows": 100
                          })

# execute the query
results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query), \
                       headers={'Authorization': 'Bearer ' + token})

print(results.json())