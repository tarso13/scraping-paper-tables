from download_html import *
import json 

# List containing the html files with tables that have been extracted 
files_extracted = []

# Value used to replace undesired word occurences in datasets
EMPTY = ''

# Map containing the (extra) url as key and the table suffix as value
url_suffixes = {}

# Get file content
def get_file_content(filepath):
    file = open(filepath, "r", encoding="utf-8")
    content = file.read()
    file.close()
    return content

# Extract all tables from html file provided in html form and extra footnotes for aanda journals
def extract_html_tables(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.findAll('table')
    return tables

# Search for footnotes in aanda articles 
def search_aanda_footnotes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    notes_section = soup.find('div', class_='history')
    
    if notes_section == None:
        return None
    
    labels = notes_section.find_all('sup')
    footnotes_kvs = {}
    
    # Extract the (a), (b), (c) labels and their text
    for label in labels:
        label_name = label.get_text(strip=True)
        label_text = label.find_next('p').get_text(strip=True)
        footnotes_kvs[label_name] = label_text
    return footnotes_kvs

# Search and extract table description and notes 
def search_aanda_table_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    notes_section = soup.find('div', class_='history')
    description_section = soup.find('div', id='annex')
    
    if notes_section == None or description_section == None:
        return None, None
    
    description = description_section.find('p').get_text(strip=True)
    notes = notes_section.find('p').get_text(strip=True)

    return description, notes 

# Search journal metadata (authors, title, date, journal) 
def search_aanda_metadata(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    metas = soup.findAll('meta')
    authors = []
    journal = ''
    title = ''
    date = ''
    for meta in metas:
        content = meta.get('content')
        name = meta.get('name')
        match name:
            case 'citation_author':
                authors.append(content)
            case 'citation_journal_title':
                journal = content
            case 'citation_title':
                title = content
            case 'citation_publication_date':
                date = content

    return authors, journal, title, date
  
def extract_aanda_metadata(html_content):
    authors, journal, title, publication_date = search_aanda_metadata(html_content)
    print(f'Authors: {str(authors)}')
    print(f'Journal: {journal}, title: {title}, publication date:{publication_date}')
    # check for footnotes (aanda case)
    footnotes = {}
    if 'A&A)_T' in title:
        footnotes = search_aanda_footnotes(html_content)
    return authors, journal, title, publication_date, footnotes

# Validates footnotes found through parsing and returns only the correct ones
def validate_aanda_footnotes(footnotes, valid_footnotes, data_found):
    if not footnotes:
        return None
    
    for footnote in footnotes:
        footnote_constraint = '(' in footnote and ')' in footnote
        for data in data_found:
            if footnote in data and footnote_constraint:
                valid_footnotes[footnote] = footnotes[footnote]
    return valid_footnotes        
    
# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
# and then converted into json files
def extract_table_data(table, title, footnotes, directory_name):
    json_data = {}
    key_prefix = f'headers'
    headers = list(th.get_text() for th in table.find("tr").find_all("th"))
    if len(headers) == 0:
        headers = list(td.get_text() for td in table.find("tr").find_all("td"))
    json_data[key_prefix] = str(headers)
    json_data[key_prefix] = json_data[key_prefix].replace(',', '')
    
    print(headers)
    valid_footnotes = {}
    for row in table.find_all("tr")[1:]:
        key_prefix = f'row{str(table.find_all("tr").index(row))}'
        data = list(td.get_text().replace('\xa0', EMPTY).replace('\n', EMPTY) for td in row.find_all("td"))      
        print(data)
        if 'A&A' in title:
           valid_footnotes = validate_aanda_footnotes(footnotes, valid_footnotes, data)
        json_data[key_prefix] = str(data)
        json_data[key_prefix] = json_data[key_prefix].replace(',', '')
    if valid_footnotes:
        print('Table contains footnotes: ')
        print(valid_footnotes)
        
    path_to_json = os.path.join(directory_name,f'{title}.json')
    file = open(path_to_json, 'w', encoding='utf-8')
    file.write(json.dumps(json_data, indent=4))

# Extract all table data found in html files in given directory and print them
# If extra links for tables are included, these links are appended in links_to_extract
# and are handled after the simple ones 
def extract_tables(directory_name):
    if os.path.exists(directory_name) == False:
        return
    
    for entry in os.listdir(directory_name):
        path_to_entry = os.path.join(directory_name, entry)
        # os.listdir returns both directories and files included in diretory given
        if os.path.isfile(path_to_entry) == False: 
            continue
            
        if entry in files_extracted:
            continue

        files_extracted.append(entry)
        
        print("\nResults for " + entry)
        entry_content = get_file_content(path_to_entry)
        tables = extract_html_tables(entry_content)
     
        if 'A&A' in entry and 'A&A)_T' not in entry:
           metadata = extract_aanda_metadata(entry_content)
           continue
       
        footnotes = search_aanda_footnotes(entry_content)
        table_description, table_notes = search_aanda_table_info(entry_content)  
        print(f'Table contains the following info:')
        print(f'Description: {str(table_description)}\nNotes: {str(table_notes)}')
  
        create_directory('json_results')
        for table in tables:
            extract_table_data(table, entry.replace('.html',''), footnotes, 'json_results')