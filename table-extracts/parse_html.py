import urllib.request
from bs4 import BeautifulSoup
import os 

# Extract all tables from url provided in html form
def extract_html_tables(html):
    print("\nResults for " + html)
    html_content =  open(html,'r', encoding='UTF8').read()
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.findAll("table")
    return tables    

# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
def extract_table_data(table):
    headers = [th.get_text() for th in table.find("tr").find_all("td")]
    print(headers)
    for row in table.find_all("tr")[1:]:
        dataset = [td.get_text() for td in row.find_all("td")]
        print(dataset)

# Extract all table data found in html files in given directory and print them
def extract_tables(directory_name):
    html_files = os.listdir(directory_name)
    for html in html_files:
        tables = extract_html_tables(directory_name + "/" + html)
        for table in tables:
            extract_table_data(table)

extract_tables("html_papers_astrophysics")