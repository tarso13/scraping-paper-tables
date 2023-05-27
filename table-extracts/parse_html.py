import urllib.request
from bs4 import BeautifulSoup

links = [
    "https://iopscience.iop.org/article/10.1086/313034/fulltext/35878.text.html",
    "https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html"
]

def fetch_data(url):
    try:
        f = urllib.request.urlopen(url)
        html = f.read()
        f.close()
        return html
    except urllib.request.HTTPError as e:
        print(e, "while fetching", url)


def extract_html_tables(link):
    print("\nResults for " + link)
    html = fetch_data(link)
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.findAll("table")
    return tables    


def extract_table_data(table):
    headers = [th.get_text() for th in table.find("tr").find_all("td")]
    print(headers)
    for row in table.find_all("tr")[1:]:
        dataset = [td.get_text() for td in row.find_all("td")]
        print(dataset)

def extract_tables():
    for link in links:
        tables = extract_html_tables(link)
        for table in tables:
            extract_table_data(table)

extract_tables()