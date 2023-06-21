from bs4 import BeautifulSoup
import urllib.request
from tldextract import extract
import os
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# List of invalid words which may be encountered in paper titles 
invalid_characters_as_words = ['#', '<', '$', '+', '%', '>', '!', '`', '*', "'", '|', '{', '?', '=', '}','/',':', '"', '\\','@']

# Create a directory with the name given (if it does not exist)
def create_directory(directory_name):
    if os.path.isdir(directory_name):
        return
    os.mkdir(directory_name)
        
# Identify the domain name and replace dots with underscores to save file locally
# Example: "http://abc.hostname.com/somethings/anything/"
def domain_from_url(url):
    tsd, td, tsu = extract(url) # abc, hostname, com
    url_domain = f'{tsd}.{td}.{tsu}'  
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
            local_file = f'{new_title}.html'
        else:
            local_file = f'{new_title}{suffix}.html'
        if local_file in downloaded_files:
            return
        print('Downloading ' + url)
        urllib.request.urlretrieve(url, f'{directory_name}/{local_file}')
        return f'{directory_name}/{new_title}.html'
    except urllib.request.HTTPError as e:
        print(e, " while retrieving ", url)


# Download html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_all_html_files(directory_name, urls):
    executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
    results = []
    for url in urls:
        try:
            new_directory_name = directory_name
            if 'aanda' in domain_from_url(url):
                new_directory_name = f'{directory_name}_aanda'
            results.append(executor.submit(download_html_locally, url, new_directory_name, fetch_title(url), ''))
        except Exception as e:
            print(e)
    # wait for all downloads to complete 
    for result in results:
        result.result()

# Download extra html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_extra_html_files(directory_name, urls_suffixes):
    executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
    results = []
    for url in urls_suffixes:
        try:
            results.append(executor.submit(download_html_locally, url, directory_name, fetch_title(url), str(urls_suffixes[url])))
        except Exception as e:
            print(e)
    # wait for all downloads to complete        
    for result in results:
        result.result()
