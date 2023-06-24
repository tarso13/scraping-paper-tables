from bs4 import BeautifulSoup
from tldextract import extract
import os
import httplib2

# List of invalid words which may be encountered in paper titles
invalid_characters_as_words = ['#', '<', '$', '+', '%', '>', '!',
                               '`', '*', "'", '|', '{', '?', '=', '}', '/', ':', '"', '\\', '@']

# Create a directory with the name given (if it does not exist)
def create_directory(directory_name):
    if os.path.isdir(directory_name):
        return
    os.mkdir(directory_name)

# Identify the domain name and replace dots with underscores to save file locally
# Example: "http://abc.hostname.com/somethings/anything/"
def domain_from_url(url):
    tsd, td, tsu = extract(url)  # abc, hostname, com
    url_domain = f'{tsd}.{td}.{tsu}'
    return url_domain

# Find html title given the content of an html file
def fetch_title(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.title.string

# Set up title for saved html
# Ignore spaces and invalid characters
def setup_title(title):
    title_no_spaces_list = str(title).replace(" ", "_")
    title_no_spaces = ''
    for word in title_no_spaces_list:
        if word not in invalid_characters_as_words:
            title_no_spaces += word
    return title_no_spaces


# Download url provided and save it locally (html file)
# The directory to save the file is provided
# The name of the file is the new title generated from the title provided
def download_html_locally(url, directory_name, suffix):
    try:
        create_directory(directory_name)
        downloaded_files = os.listdir(directory_name)
        print('Downloading ' + url)
        http = httplib2.Http()
        _, content = http.request(url)
        new_title = setup_title(fetch_title(content))
        
        local_file = ''
        if suffix == '':
            local_file = f'{new_title}.html'
        else:
            local_file = f'{new_title}{suffix}.html'
            
        if local_file in downloaded_files:
            return
        
        with open(f'{directory_name}/{local_file}', 'wb') as file:
            file.write(content)
    except httplib2.HttpLib2Error as e:
        print(e, " while retrieving ", url)


# Download html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_all_html_files(directory_name, urls):
    for url in urls:
        new_directory_name = directory_name
        if 'aanda' in domain_from_url(url):
            new_directory_name = f'{directory_name}_aanda'
        download_html_locally(url, new_directory_name, '')

# Download extra html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_extra_html_files(directory_name, urls_suffixes):
    for url in urls_suffixes:
        download_html_locally(url, directory_name, str(urls_suffixes[url]))