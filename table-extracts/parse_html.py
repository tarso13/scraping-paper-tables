import urllib.request
from bs4 import BeautifulSoup

links = [
    "https://iopscience.iop.org/article/10.1086/313034/fulltext/35878.text.html",
    "https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html",
]

def fetch_data(url):
    try:
        f = urllib.request.urlopen(url)
        html = f.read()
        f.close()
        return html
    except urllib.request.HTTPError as e:
        print(e, "while fetching", url)


def get_table_data():
    html = None
    for link in links:
        html = fetch_data(link)
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.findAll("table")
        for table in tables:
            print(table)

get_table_data()
