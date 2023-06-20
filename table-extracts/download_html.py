from bs4 import BeautifulSoup
import urllib.request
from tldextract import extract
import os

# List of invalid words which may be encountered in paper titles 
invalid_characters_as_words = ['#', '<', '$', '+', '%', '>', '!', '`', '*', "'", '|', '{', '?', '=', '}','/',':', '"', '\\','@']

# Links to extract data from 
urls = [
    'https://iopscience.iop.org/article/10.1086/313034/fulltext/35878.text.html',
    'https://www.aanda.org/articles/aa/full_html/2018/08/aa32766-18/aa32766-18.html',
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44220-22/aa44220-22.html', 
    'https://www.aanda.org/articles/aa/full_html/2023/06/aa44161-22/aa44161-22.html',
    'https://www.aanda.org/articles/aa/full_html/2016/02/aa27620-15/aa27620-15.html',
    'https://www.aanda.org/articles/aa/full_html/2016/01/aa26356-15/aa26356-15.html'
]

# Create a directory with the name given (if it does not exist)
def create_directory(directory_name):
    if os.path.isdir(directory_name):
        return
    else:
        os.mkdir(directory_name)
        
# Identify the domain name and replace dots with underscores to save file locally
# Example: "http://abc.hostname.com/somethings/anything/"
def domain_from_url(url):
    tsd, td, tsu = extract(url) # abc, hostname, com
    url_domain = tsd + '_' + td + '_' + tsu  
    return url_domain

# Open url provided and return fetched data (html file)
def fetch_title(url):
    try:
        f = urllib.request.urlopen(url)
        html = f.read()
        f.close()
        soup = BeautifulSoup(html, "html.parser")
        return soup.title.string
    except urllib.request.HTTPError as e:
        print(e, " while fetching ", url)

# Set up title for saved html 
# Ignore spaces and invalid characters
def setup_title(title):
    title_no_spaces_list = title.replace(" ", "_")
    title_no_spaces = ''
    for word in title_no_spaces_list:
        if word not in invalid_characters_as_words:
            title_no_spaces += word
    return title_no_spaces
    

# Download url provided and save it locally (html file)
# The directory to save the file is provided
# The name of the file is the new title generated from the title provided
def download_html_locally(url, directory_name, title, suffix):
    try:
        create_directory(directory_name)
        downloaded_files = os.listdir(directory_name)
        new_title = setup_title(title)
        local_file = ''
        if suffix == '':
            local_file = new_title + ".html"
        else:
            local_file = new_title + suffix + ".html"
        if local_file in downloaded_files:
            return
        print('Downloading ' + url)
        urllib.request.urlretrieve(url, directory_name + "/" + local_file)
        return directory_name + "/" + new_title + ".html"
    except urllib.request.HTTPError as e:
        print(e, " while retrieving ", url)


# Download html files from urls and save them locally
# Specify aanda case and save those files in different directory
def download_all_html_files():
    for url in urls:
        if 'aanda' in url:
            download_html_locally(url, 'html_papers_astrophysics_aanda', fetch_title(url), '')
            continue
        download_html_locally(url, 'html_papers_astrophysics', fetch_title(url), '')
        