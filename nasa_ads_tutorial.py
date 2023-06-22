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
                           "fl": "bibcode",
                           "rows": 1
                          })

# execute the query
bibecode_results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query), \
                       headers={'Authorization': 'Bearer ' + token})

# Extract bibcode from json results
json_results = bibecode_results.json()
json_response = json_results['response']
json_docs = json_response['docs']
bibcode_kv = str(json_docs[0])
position = bibcode_kv.find(": '")
final_bibcode = bibcode_kv[position + 3 : bibcode_kv.find("'}")]

# download the arXiv html
url_results = requests.get(f'https://ui.adsabs.harvard.edu/link_gateway/{final_bibcode}/PUB_HTML') 

# write the output to file
with open('html_content.html', 'wb') as f:
    f.write(url_results.content)

# show where the ADS URL redirected to
print(f'Url found for html: {url_results.url}')