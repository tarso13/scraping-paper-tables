import urllib.request
from bs4 import BeautifulSoup
from download_html import urls
from download_html import download_html_locally
from download_html import fetch_title
import os

files_extracted = []
links_to_extract = []

# Extract all tables from url provided in html form
def extract_html_tables(html):
    print("\nResults for " + html)
    html_content = open(html, "r", encoding="UTF8").read()
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.findAll("table")
    return tables


# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
def extract_table_data(table, header_type):
    headers = list(th.get_text() for th in table.find("tr").find_all("th"))
    print(headers)
    for row in table.find_all("tr")[1:]:
        dataset = list(td.get_text() for td in row.find_all("td"))
        print(dataset)


# Extract all table data found in html files without included extra links for tables in given directory and print them
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
                print("Normal case found")
                # Note: You need to define the header declaration type in html file
                # For example in https://iopscience.iop.org/article/10.1086/313034/fulltext/35878.text.html it is: 'td'
                # whereas in  https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html it is: 'th'
                extract_table_data(table, 'th')


def find_nth_occurence(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)


def domain(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    base = soup.find("base")
    base_href = base["href"]
    # We want the third occurence of '/'
    # the first belongs to the https scheme (https://site.org/path_to_html.html)
    # the // is counted as 1
    position_of_slash = find_nth_occurence(base_href, "/", 2)
    domain = base_href[0:position_of_slash]
    return domain


def extract_extra_tables_from_html_files(directory_name):
    print("Extra files found " + str(len(links_to_extract)))
    # if there was a reference to tables in extra files we retrieve the extra files as well
    if len(links_to_extract) != 0:
        for html in links_to_extract:
            html_content = open(
                directory_name + "/" + html, "r", encoding="utf-8"
            ).read()

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
                    print(domain_found + a["href"])
                    download_html_locally(
                        domain_found + a["href"],
                        directory_name,
                        title,
                        "T" + str(counter),
                    )
                    extract_tables(directory_name)


extract_tables("html_papers_astrophysics")
extract_extra_tables_from_html_files("html_papers_astrophysics")
