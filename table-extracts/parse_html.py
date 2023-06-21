from download_html import *
from urllib.parse import urlparse

# List containing the html files with tables that have been extracted 
files_extracted = []

# List containing the (extra) html files with tables to be extracted 
files_to_extract = []

# Value used to replace undesired word occurences in datasets
EMPTY = ''

# Map containing the (extra) url as key and the table suffix as value
url_suffixes = {}

# Identify the domain name given an html content using the base href tag
# and the occurences of '/'
# Example: https://site.org/path_to_html.html
# Note: // is counted as 1
def domain(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    base = soup.find('base')
    base_href = base['href']
    domain = urlparse(base_href).netloc
    return domain

# Extract all tables from html file provided in html form
def extract_html_tables(html):
    print("\nResults for " + html)
    html_file = open(html, "r", encoding="UTF8")
    html_content = html_file.read()
    html_file.close()
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.findAll("table")
    return tables


# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
def extract_table_data(table):
    headers = list(th.get_text() for th in table.find("tr").find_all("th"))
    if len(headers) == 0:
        headers = list(td.get_text() for td in table.find("tr").find_all("td"))

    print(headers)
    for row in table.find_all("tr")[1:]:
        dataset = list(td.get_text().replace('\xa0', EMPTY).replace('\n', EMPTY) for td in row.find_all("td"))      
        print(dataset)


# Extract all table data found in html files in given directory and print them
# If extra links for tables are included, these links are appended in links_to_extract
# and are handled after the simple ones 
def extract_tables(directory_name):
    html_files = os.listdir(directory_name)
    
    for html in html_files:
        if html in files_extracted:
            continue

        files_extracted.append(html)
        
        if html in files_to_extract:
            files_to_extract.remove(html)
            
        if 'A&A' in html and 'A&A)_T' not in html: # first aanda case containing the links
            aanda_parser(directory_name, html)
            continue
       
        tables = extract_html_tables(f'{directory_name}/{html}')

        for table in tables:
            extract_table_data(table)

# Extract all table data found in html files with references to other htmls (aanda case) containing the actual tables
# When extra links are identified, then the tables are extracted using extract_tables
# The name of the extra files is the same as the initial html files concatenated with '_T#', where # is the number of the extra link
def extract_aanda_tables_from_html_files(directory_name):
    extract_tables(directory_name)
    download_extra_html_files(directory_name, url_suffixes)
    if len(files_to_extract) != 0:
        extract_tables(directory_name)

# Build table suffix for local html file that contains extra table found in original html
def table_suffix(path_to_table):
    suffix_index  = path_to_table.find('/T')
    html_index  = path_to_table.find('.html')
    suffix = path_to_table[suffix_index:html_index]
    suffix = suffix.replace('/', '_')
    return suffix

# Parser specifically for html papers of aanda.org
# The format of papers in this domain includes tables in extra links
def aanda_parser(directory_name, html):
    html_file = open(f'{directory_name}/{html}', 'r', encoding='UTF8')
    html_content = html_file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    domain_found = domain(html_content)
    table_classes = soup.findAll('div', {'class' : 'ligne'})
    
    for table_class in table_classes:   
        path_to_table = table_class.find('a')['href']
        full_path = f'https://{domain_found}{path_to_table}'
        title = setup_title(fetch_title(full_path))
        suffix = table_suffix(path_to_table)
        html_local_path = f'{title}{suffix}.html'
        url_suffixes[full_path] = suffix
        
        if html_local_path not in files_to_extract:
            print(f'Need to download {full_path}')
            files_to_extract.append(html_local_path)