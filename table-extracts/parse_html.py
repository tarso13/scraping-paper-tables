import urllib.request
from bs4 import BeautifulSoup

# Links to extract data from (temporary solution)
urls = [
    "https://iopscience.iop.org/article/10.1086/313034/fulltext/35878.text.html",
    "https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html"
]

# Open url provided and return fetched data (html file)
def fetch_data(url):
    try:
        f = urllib.request.urlopen(url)
        html = f.read()
        f.close()
        return html
    except urllib.request.HTTPError as e:
        print(e, "while fetching", url)

# Extract all tables from url provided in html form
def extract_html_tables(url):
    print("\nResults for " + url)
    html = fetch_data(url)
    soup = BeautifulSoup(html, "html.parser")
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

# Extract all table data found in given html links and print them
def extract_tables():
    for url in urls:
        tables = extract_html_tables(url)
        for table in tables:
            extract_table_data(table)

extract_tables()