from bs4 import BeautifulSoup
from parse_html import extract_table_data, extract_journal_metadata, search_aanda_footnotes, search_aanda_journal_metadata,search_aanda_table_info, extract_html_tables, title_to_metadata, index_parent, append_to_elastic_index, upload_new_index, doc_index_id
from tldextract import extract
from urllib.parse import urlparse
import os
import requests

# Headers to be used when retrieving urls 
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

# List of invalid words which may be encountered in paper titles
invalid_characters_as_words = ['#', '<', '$', '+', '%', '>', '!', '.',
                               '`', '*', "'", '|', '{', '?', '=', '}', '/', ':', '"', '\\', '@', ',']

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
    soup = BeautifulSoup(html_content, 'html.parser')
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
def download_html_locally(url, directory_name, suffix, download_extra_files):
    try:
        create_directory(directory_name)
        downloaded_files = os.listdir(directory_name)
        print('Downloading ' + url)
        response = requests.get(url, headers=headers)
        content = response.text
        new_title = setup_title(fetch_title(content))
        if 'iopscience' in directory_name and 'IOPscience' not in new_title:
            new_title = f'{new_title}_IOPscience'
        
        local_file = f'{new_title}{suffix}.html'
                
        if local_file in downloaded_files:
            print(f'Cancel download of {url} [Already exists]')
            return
        
        path_to_file = os.path.join(directory_name, local_file)

        with open(path_to_file, 'w', encoding='utf-8') as file:
            file.write(content)
        
        if 'A&A' in local_file and 'A&A)_T' not in local_file:
          path_to_extra_file = f'{os.path.join(directory_name, directory_name)}_tables'
          aanda_download_extra_files(content, path_to_extra_file, downloaded_files, download_extra_files)
    except requests.RequestException as e:
        print(str(e), ' while retrieving ', url)


# Download html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_all_html_files(directory_name, urls, download_extra_files):
    for url in urls:
        new_directory_name = directory_name
        if 'aanda' in domain_from_url(url):
            new_directory_name = f'{directory_name}_aanda'
        if 'iopscience' in domain_from_url(url):
            new_directory_name = f'{directory_name}_iopscience'
        download_html_locally(url, new_directory_name, '', download_extra_files)
        
# Build table suffix for local html file that contains extra table found in original html
def table_suffix(path_to_table):
    suffix_index  = path_to_table.find('/T')
    html_index  = path_to_table.find('.html')
    suffix = path_to_table[suffix_index:html_index]
    suffix = suffix.replace('/', '_')
    return suffix

# Identify the domain name given an html content using the base href tag
def domain(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    base = soup.find('base')
    base_href = base['href']
    domain = urlparse(base_href).netloc
    return domain

# Find extra table files from initial aanda papers and download them
def aanda_download_extra_files(content, directory_name, downloaded_files, download_extra_files):
    soup = BeautifulSoup(content, 'lxml')
    table_classes = soup.findAll('div', {'class' : 'ligne'})
    url_suffixes = {}
    domain_found = domain(content)
    title = setup_title(fetch_title(content))
    title_to_metadata[title] = extract_journal_metadata(soup)
    for table_class in table_classes:   
        path_to_table = table_class.find('a')['href']
        full_path = f'https://{domain_found}{path_to_table}'
        suffix = table_suffix(path_to_table)
        if not download_extra_files:
            response = requests.get(full_path, headers=headers)
            content = response.text
            extract_undownloaded_tables(content, f'{title}{suffix}', title)   
            continue                                        
        html_local_path = f'{title}{suffix}.html'
        url_suffixes[full_path] = suffix
        
        if html_local_path in downloaded_files:
            url_suffixes.pop(full_path)
        
    download_extra_html_files(directory_name, url_suffixes, download_extra_files)
            
# Download extra html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_extra_html_files(directory_name, url_suffixes, download_extra_files):
    for url in url_suffixes:
        download_html_locally(url, directory_name, str(url_suffixes[url]), download_extra_files)
        
# Extract all table data found in html content without downloading the extra files and print them
def extract_undownloaded_tables(content, title, entry):
    parent_index = ''
    soup_content = BeautifulSoup(content, 'html.parser')
    
    tables, _ = extract_html_tables(soup_content)
    
    parent_index = 'astro'
    parent_index_id = 0
    footnotes = None
    metadata = {}
    extra_metadata = {}
    table_info = {}
    
    if 'A&A' in title:
        footnotes =  search_aanda_footnotes(soup_content)
        table_info = search_aanda_table_info(soup_content)
        metadata = search_aanda_journal_metadata(entry)
    
    parent_index_id = 1   
    index_parent(parent_index, parent_index_id)
            
    for table in tables:
        index = tables.index(table)

        global doc_index_id 
        doc_index_id += 1

        json_data = extract_table_data(table, title, footnotes, metadata, extra_metadata, table_info, index, 'false')
        append_to_elastic_index(parent_index, doc_index_id, json_data)
    