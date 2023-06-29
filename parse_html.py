from download_html import *
import json 

# List containing the html files with tables that have been extracted 
files_extracted = []

# List containing the (extra) html files with tables to be extracted 
files_to_extract = []

# Value used to replace undesired word occurences in datasets
EMPTY = ''

# Map containing the (extra) url as key and the table suffix as value
url_suffixes = {}

# Extract all tables from html file provided in html form and extra footnotes for aanda journals
def extract_html_tables(html):
    print("\nResults for " + html)
    
    html_file = open(html, "r", encoding="utf-8")
    html_content = html_file.read()
    html_file.close()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    tables = soup.findAll('table')
    footnotes = {}
    # check for footnotes (aanda case)
    if 'A&A)_T' in html:
        footnotes = search_aanda_footnotes(html_content)
    
    return tables, footnotes

# Search for footnotes in aanda articles 
def search_aanda_footnotes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    history_div = soup.find('div', class_='history')
    
    if history_div == None:
        return
    
    labels = history_div.find_all('sup')
    footnotes_kvs = {}
    # Extract the (a), (b), (c) labels and their text
    for label in labels:
        label_name = label.get_text(strip=True)
        label_text = label.find_next('p').get_text(strip=True)
        footnotes_kvs[label_name] = label_text
    return footnotes_kvs
        
        
# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
# and then converted into json files
# Only valid footnotes found are returned
def extract_table_data(table, title, footnotes, directory_name):
    json_data = {}
    key_prefix = f'headers'
    headers = list(th.get_text() for th in table.find("tr").find_all("th"))
    if len(headers) == 0:
        headers = list(td.get_text() for td in table.find("tr").find_all("td"))
    json_data[key_prefix] = str(headers).replace('[', '').replace(']','')
    json_data[key_prefix] = json_data[key_prefix].replace(',', '')
    
    print(headers)
    valid_footnotes = {}
    for row in table.find_all("tr")[1:]:
        key_prefix = f'dataset{str(table.find_all("tr").index(row))}'
        dataset = list(td.get_text().replace('\xa0', EMPTY).replace('\n', EMPTY) for td in row.find_all("td"))      
        print(dataset)
        
        if footnotes:
            for footnote in footnotes:
                footnote_constraint = '(' in footnote and ')' in footnote
                for data in dataset:
                    if footnote in data and footnote_constraint:
                        valid_footnotes[footnote] = footnotes[footnote]
        json_data[key_prefix] = str(dataset).replace('[', '').replace(']','')
        json_data[key_prefix] = json_data[key_prefix].replace(',', '')
    path_to_json = os.path.join(directory_name,f'{title}.json')
    file = open(path_to_json, 'w', encoding='utf-8')
    file.write(json.dumps(json_data, indent=4))
    return valid_footnotes


# Extract all table data found in html files in given directory and print them
# If extra links for tables are included, these links are appended in links_to_extract
# and are handled after the simple ones 
def extract_tables(directory_name):
    if os.path.exists(directory_name) == False:
        return
    
    for entry in os.listdir(directory_name):
        path_to_entry = os.path.join(directory_name, entry)
        if os.path.isfile(path_to_entry) == False: # os.listdir returns both directories and files included in diretory given
            continue
            
        if entry in files_extracted:
            continue

        files_extracted.append(entry)
        
        if entry in files_to_extract:
            files_to_extract.remove(entry)
            
        if 'A&A' in entry and 'A&A)_T' not in entry:
            continue
        
        tables, footnotes = extract_html_tables(path_to_entry)
        create_directory('json_results')
        for table in tables:
            footnotes_in_table = extract_table_data(table, entry.replace('.html',''), footnotes, 'json_results')
            if len(footnotes_in_table):
                print('Table contains footnotes: ')
                print(footnotes_in_table)