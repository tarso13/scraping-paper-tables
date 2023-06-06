from bs4 import BeautifulSoup
import urllib.request
import os

# List of invalid words which may be encountered in paper title 
invalid_characters_as_words = ['#', '<', '$', '+', '%', '>', '!', '`', '&', '*', "'", '|', '{', '?', '=', '}','/',':', '"', '\\','@']

# Links to extract data from (temporary solution)
urls = [
    "https://iopscience.iop.org/article/10.1086/313034/fulltext/35878.text.html",
    "https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html",
]

# Create a directory with the name given (if it does not exist)
def create_directory(directory_name):
    if os.path.isdir(directory_name):
        return
    else:
        os.mkdir(directory_name)

# Open url provided and return fetched data (html file)
def fetch_title(url):
    try:
        f = urllib.request.urlopen(url)
        html = f.read()
        f.close()
        soup = BeautifulSoup(html, "html.parser")
        return soup.find('title').get_text()
    except urllib.request.HTTPError as e:
        print(e, " while fetching ", url)

# Set up title for saved html 
# Ignore spaces and invalid characters
def setup_title(title):
    title_no_spaces_list = list(map(str.strip, title.split(' ')))
    title_no_spaces = ''
    for word in title_no_spaces_list:
        if(invalid_characters_as_words.__contains__(word) == False):
            title_no_spaces += word
    return title_no_spaces
    

# Download url provided and save it locally (html file)
# The directory to save the file is provided
# The name of the file is the new title generated from the title provided
def download_html_locally(url, directory_name, title):
    try:
        create_directory(directory_name)
        new_title = setup_title(title)
        urllib.request.urlretrieve(url, directory_name + "/" + new_title + ".html")
    except urllib.request.HTTPError as e:
        print(e, " while retrieving ", url)


# Download html files from urls and save them locally
def download_all_html_files():
    for url in urls:
        download_html_locally(url, "html_papers_astrophysics", title=fetch_title(url))

download_all_html_files()