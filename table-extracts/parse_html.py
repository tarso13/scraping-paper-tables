from bs4 import BeautifulSoup
from download_html import download_html_locally
from download_html import fetch_title, setup_title
import os

# List containing the html files with tables that have been extracted 
files_extracted = []

# List containing the (extra) html files with tables to be extracted 
files_to_extract = []

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
        dataset = list(td.get_text().replace(u'\xa0', u' ').replace('\n',' ') for td in row.find_all("td"))      
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
        
        if 'A&A' in html and 'A&A)_T' not in html: # first aanda case containing the links
            aanda_parser(directory_name, html)
            return
            
        tables = extract_html_tables(directory_name + "/" + html)

        for table in tables:
            extract_table_data(table)


# Find the n-th occurence of a substring in a string
def find_nth_occurence(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)


# Identify the domain name given an html content using the base href tag
# and the occurences of '/'
# Example: https://site.org/path_to_html.html
# Note: // is counted as 1
def domain(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    base = soup.find('base')
    base_href = base['href']
    position_of_slash = find_nth_occurence(base_href, "/", 2)
    domain = base_href[0:position_of_slash]
    return domain

# Extract all table data found in html files with references to other htmls (aanda case) containing the actual tables
# When extra links are identified, then the tables are extracted using extract_tables
# The name of the extra files is the same as the initial html files concatenated with '_T#', where # is the number of the extra link
def extract_extra_tables_from_html_files(directory_name):
    for html in files_to_extract:
        extract_tables(directory_name)
        files_to_extract.remove(html)

# Parser specifically for html papers of aanda.org
# The format of papers in this domain includes tables in extra links
def aanda_parser(directory_name, html):
    html_file = open(directory_name + '/' + html, "r", encoding="UTF8")
    html_content = html_file.read()
    html_file.close()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    domain_found = str(domain(html_content))
    
    table_classes = soup.findAll('div', {'class' : 'ligne'})
    
    for table_class in table_classes:
        path_to_table = table_class.find('a')['href']
        
        if path_to_table == None: # normal case (we are in the extra tables)
            extract_tables(directory_name)
            
        full_path = domain_found + path_to_table
        position_of_slash = find_nth_occurence(path_to_table, '/', 6)
        title = setup_title(fetch_title(full_path))
        suffix  = '_' + path_to_table[position_of_slash+1 : len(path_to_table)]
        suffix = suffix.replace('.html', '')
        
        download_html_locally(
            full_path,
            directory_name,
            title, 
            suffix
        )
        files_to_extract.append(title + suffix + '.html')

extract_tables('html_papers_astrophysics')
extract_extra_tables_from_html_files('html_papers_astrophysics')