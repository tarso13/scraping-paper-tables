from bs4 import BeautifulSoup
from download_html import download_html_locally
from download_html import fetch_title
import os

# List containing the html files containing tables that have been extracted 
files_extracted = []

# List containing the (extra) html files containing tables to be extracted 
links_to_extract = []

# Extract all tables from html file provided in html form
def extract_html_tables(html):
    print("\nResults for " + html)
    html_content = open(html, "r", encoding="UTF8").read()
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.findAll("table")
    return tables


# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
def extract_table_data(table):
    headers = list(th.get_text() for th in table.find("tr").find_all("th"))
    if len(headers) == 0:
        headers = list(td.get_text() for td in table.find("tr").find_all("td"))
    print(headers)
    for row in table.find_all("tr")[1:]:
        dataset = list(td.get_text().replace(u'\xa0', u' ') for td in row.find_all("td"))
        print(dataset)


# Extract all table data found in html files in given directory and print them
# If extra links for tables are included, these links are appended in links_to_extract
# and are handled after the simple ones
def extract_tables(directory_name):
    html_files = os.listdir(directory_name)
    for html in html_files:
        tables = extract_html_tables(directory_name + "/" + html)
        for table in tables:
            extra_link = table.find("a")
            if extra_link and (".html" in extra_link["href"]):
                if html not in links_to_extract:
                    links_to_extract.append(html)
            else:
                extract_table_data(table)


# Find the n-th occurence of a substring in a string
def find_nth_occurence(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)


# Identify the domain name given an html content using the base href tag
# and the occurences of '/'
# Example: https://site.org/path_to_html.html
# Note: // is counted as 1
def domain(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    base = soup.find("base")
    base_href = base["href"]
    position_of_slash = find_nth_occurence(base_href, "/", 2)
    domain = base_href[0:position_of_slash]
    return domain

# Extract all table data found in html files with references to other htmls containing the actual tables
# When extra links are identified, then the tables are extracted using extract_tables
# The name of the extra files is the same as the initial html files concatenated with '_T#', where # is the number of the extra link
def extract_extra_tables_from_html_files(directory_name):
    if len(links_to_extract) == 0:
        return
    for html in links_to_extract:
        html_content = open(directory_name + "/" + html, "r", encoding="UTF8").read()

        domain_found = str(domain(html_content))
        soup = BeautifulSoup(html_content, "html.parser").findAll(
            lambda t: t.name == "a" and t.text.startswith("Table")
        )
        counter = 0
        hrefs_found = []
        for a in soup:
            html_file = ".html" in a["href"]
            non_contents_html_file = "contents" not in a["href"]
            if html_file and non_contents_html_file:
                if hrefs_found.__contains__(a["href"]) == True:
                    continue
                hrefs_found.append(a["href"])
                counter += 1
                title = fetch_title(domain_found + a["href"])
                download_html_locally(
                    domain_found + a["href"],
                    directory_name,
                    title,
                    "_T" + str(counter),
                )
                extract_tables(directory_name)
                links_to_extract.remove(html)


extract_tables("html_papers_astrophysics")
extract_extra_tables_from_html_files("html_papers_astrophysics")