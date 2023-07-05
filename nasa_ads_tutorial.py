from password import get_password
import requests
from urllib.parse import urlencode

# get token for nasa api
token=get_password('nasa_ads_token.txt')

# Build ads encoded query using the arguments provided
# It is necessary that all of the arguments are provided and in a valid way
# Start and end year are optional, constraint specifies the search query
# If query is a journal, provide 'bibstem:ABC', where ABC is the journal abbrevation for ads
# which can be found here: https://adsabs.harvard.edu/abs_doc/journals1.html#
# If query is an author, use 'author:full_name' or 'full_name'
# For more info about what can be used as a query, use this guide: https://ui.adsabs.harvard.edu/help/search/
def build_ads_query(query_constraint, start_year, end_year, return_value, results):
    query = {}
    if start_year == None or end_year == None:
        query = {"q": query_constraint, "fl": return_value, "rows": results}
    else:
        period_of_time = f'year:[{str(start_year)} TO {str(end_year)}]'
        query = {"q": query_constraint, "fq": period_of_time, "fl": return_value, "rows": results}
    encoded_query = urlencode(query)
    return encoded_query

# Execute ads query and return the results
def get_ads_query_results(encoded_query):
    query_results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query), \
                        headers={'Authorization': 'Bearer ' + token})
    return query_results

# Extract bibcode from ads query json results
# Number of results is the amount of results expected from previous query 
def extract_bibcode_from_results(query_results, number_of_results):
    bibcodes = []
    json_results = query_results.json()
    json_response = json_results['response']
    json_docs = json_response['docs']
    # extract bibcode bibcode kv is in the form:
    # { "bibcode" : 'xxxxxxxxxx'}
    for i in range(number_of_results):
        bibcode_kv = str(json_docs[i])
        position = bibcode_kv.find(": '")
        final_bibcode = bibcode_kv[position + 3 : bibcode_kv.find("'}")]
        bibcode_kv.replace(final_bibcode,'')
        bibcodes.append(final_bibcode)
        i += 1
    return bibcodes


# Extract single ads url for given bibcode and format
# Note: format should either be "HTML" or "PDF" (Use capital letters in order for api to work)
def extract_url_from_bibcode(bibcode, format):
    url_results = requests.get(f'https://ui.adsabs.harvard.edu/link_gateway/{bibcode}/PUB_{format}') 
    return url_results.url

# Extract ads urls for given bibcodes and format
# Bibcodes is a list with bibcodes to be extracted
# Note: format should either be "HTML" or "PDF" (Use capital letters in order for api to work)
def extract_urls_from_bibcodes(bibcodes, format):
    for bibcode in bibcodes:
        url = extract_url_from_bibcode(bibcode, format)
        print(f'ADS result #{str(bibcodes.index(bibcode) + 1)}: {url}')

# A simple example of building an ads query to get url for an aanda journal published 
# between 2020 and 2023
def main():
    constraint = 'bibstem:A&A'
    number_of_results = 15
    format = 'HTML'
    ads_query = build_ads_query(constraint, 2020, 2023, 'bibcode', number_of_results)
    ads_query_results = get_ads_query_results(ads_query)
    bibcodes = extract_bibcode_from_results(ads_query_results, number_of_results)
    extract_urls_from_bibcodes(bibcodes, format)
    
main()