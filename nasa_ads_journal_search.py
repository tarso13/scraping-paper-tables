from password import get_password
import requests
from urllib.parse import urlencode
import os

format = "HTML"

# Get token for nasa api
token = get_password("nasa_ads_token.txt")

# Flag for open access journals
# If set to false, searches will return both open access and non open access journals
open_access_property = True

# It is necessary that all of the arguments are provided and in a valid way
# For more info about what can be used as a query, use this guide: https://ui.adsabs.harvard.edu/help/search/


# Search ads journal by keyword
# Return value is what the user wants to retrive, e.g. title, bibcode, etc.
# whilst results is the number of results (up to 2000)
def search_ads_by_keyword(keyword, return_value, results):
    fields = ""
    if open_access_property:
        fields = f"{return_value} property:pub_openaccess"
    else:
        fields = return_value
    query = {"q": f"abs:{keyword}", "fl": fields, "rows": results}
    encoded_query = urlencode(query)
    query_results = get_ads_query_results(encoded_query)
    bibcodes = extract_bibcode_from_results(query_results, results)
    urls = extract_urls_from_bibcodes(bibcodes, format)
    return urls


# Search ads journal by its abbreviation for ads
# which can be found here: https://adsabs.harvard.edu/abs_doc/journals1.html#
# Return value is what the user wants to retrive, e.g. title, bibcode, etc.
# whilst results is the number of results (up to 2000)
def search_ads_by_journal(journal_abbr, return_value, results):
    fields = ""
    if open_access_property:
        fields = f"{return_value} property:pub_openaccess"
    else:
        fields = return_value
    query = {
        "q": f"bibstem:{journal_abbr}",
        "fl": fields,
        "rows": results,
    }
    encoded_query = urlencode(query)
    query_results = get_ads_query_results(encoded_query)
    bibcodes = extract_bibcode_from_results(query_results, results)
    urls = extract_urls_from_bibcodes(bibcodes, format)
    return urls


# Search ads journal by its abbreviation for ads in specific period of time
# which can be found here: https://adsabs.harvard.edu/abs_doc/journals1.html#
# Return value is what the user wants to retrive, e.g. title, bibcode, etc.
# whilst results is the number of results (up to 2000)
# file is an optional parameter in case the results need to be written to a file
def search_ads_journal_by_period_of_time(
    journal_abbr, start_year, end_year, return_value, results, file
):
    period_of_time = f"year:[{str(start_year)} TO {str(end_year)}]"
    fields = ""
    if open_access_property:
        fields = f"{return_value} property:pub_openaccess"
    else:
        fields = return_value
    query = {
        "q": f"bibstem:{journal_abbr}",
        "fq": period_of_time,
        "fl": fields,
        "rows": results,
    }
    encoded_query = urlencode(query)
    query_results = get_ads_query_results(encoded_query)
    bibcodes = extract_bibcode_from_results(query_results, results)
    urls = extract_urls_from_bibcodes(bibcodes, format, file)
    return urls


# Execute ads query and return the results
def get_ads_query_results(encoded_query):
    query_results = requests.get(
        "https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query),
        headers={"Authorization": "Bearer " + token},
    )
    return query_results


# Extract bibcode from ads query json results
# Number of results is the amount of results expected from previous query
def extract_bibcode_from_results(query_results, number_of_results):
    bibcodes = []
    json_results = query_results.json()
    if not "response" in json_results:
        print("No papers were found!")
        return bibcodes
    json_response = json_results["response"]
    # print(json_response)
    json_docs = json_response["docs"]
    # print(json_docs)
    if not len(json_docs):
        print("No papers were found!")
        return bibcodes
    # extract bibcode bibcode kv is in the form:
    # { "bibcode" : 'xxxxxxxxxx'}
    for i in range(number_of_results):
        bibcode_kv = str(json_docs[i])
        position = bibcode_kv.find(": '")
        final_bibcode = bibcode_kv[position + 3 : bibcode_kv.find("'}")]
        bibcode_kv.replace(final_bibcode, "")
        bibcodes.append(final_bibcode)
        i += 1
    return bibcodes


# Extract single ads url for given bibcode and format
# Note: format should either be "HTML" or "PDF" (Use capital letters in order for api to work)
def extract_url_from_bibcode(bibcode, format):
    generated_url = f"https://ui.adsabs.harvard.edu/link_gateway/{bibcode}/PUB_{format}"
    url_results = ""
    try:
        url_results = requests.get(generated_url)
    except:
        if url_results == "":
            return None
    if url_results.url == generated_url:
        print("There is no available html for this journal.")
        return None
    # print(f'"{url_results.url}",')
    return url_results.url


# Extract ads urls for given bibcodes and format
# Bibcodes is a list with bibcodes to be extracted
# File is an optional parameter specifying a file to write the urls
# Note: format should either be "HTML" or "PDF" (Use capital letters in order for api to work)
def extract_urls_from_bibcodes(bibcodes, format, file):
    urls = []
    for bibcode in bibcodes:
        url = extract_url_from_bibcode(bibcode, format)
        urls.append(url)
        if file:
            bibcode_index = bibcodes.index(bibcode)
            if bibcode_index == len(bibcodes) - 1:
                write_url_to_file(file, url, True)
            else:
                write_url_to_file(file, url, False)
        print(url)
    return urls


# Initialize and create the file for writing
def initialize_and_open_file(directory, filename):
    file_path = os.path.join(directory, filename)
    f = open(file_path, "w")
    return f


# Write url to file
# Each line is a url
def write_url_to_file(file, url, last_url):
    file.write(url + "\n")
    if last_url:
        file.close()


# A simple example of seraching for 15 journals
# a) by keyword
# b) by journal type
# c) by journal in specific period of time
# using the nasa/ads api
def main():
    number_of_results = 2000

    # print("Searching by keyword...")
    # keyword_results = search_ads_by_keyword("SNR", "bibcode", number_of_results)
    # print(keyword_results)

    # print("Searching by journal...")
    # journal_results = search_ads_by_journal("A&A", "bibcode", number_of_results)
    # print(journal_results)

    print("Searching by journal (A&A) in specific period of time...")
    directory_name = "table-extracts"
    filename = "aanda_2022.txt"
    aanda_file = initialize_and_open_file(directory_name, filename)
    journal_time_results = search_ads_journal_by_period_of_time(
        "A&A", 2022, 2022, "bibcode", 2, aanda_file
    )
    # print(journal_time_results)

    print("Searching by journal (MNRAS) in specific period of time...")
    filename = "mnras_2022.txt"
    mnras_file = initialize_and_open_file(directory_name, filename)
    journal_time_results = search_ads_journal_by_period_of_time(
        "MNRAS", 2022, 2022, "bibcode", number_of_results, mnras_file
    )

    # print(journal_time_results)
    # write_urls_to_file("mnras_2022.txt", "table-extracts", journal_time_results)

    # print("Searching by journal...")
    # journal_results = search_ads_by_journal("A&A", "bibcode", number_of_results)
    # print(journal_results)


main()
