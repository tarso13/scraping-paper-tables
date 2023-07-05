from download_html import *
import json
from upload_elastic_index import *

# List containing the html files with tables that have been extracted
files_extracted = []

# Value used to replace undesired word occurences in datasets
EMPTY = ''

# Map containing the (extra) url as key and the table suffix as value
url_suffixes = {}

# Map containing the initial aanda title as key with its metadata as value
title_to_metadata = {}

# Get file content
def get_file_content(filepath):
    file = open(filepath, "r", encoding="utf-8")
    content = file.read()
    file.close()
    return content

# Replace sup tags with '^' indicating power exponentiation
# Span text is replaced with the expression combining both the span tag content as well as the sup tag contents
def replace_sup_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    span_tags = soup.find_all('span', class_='simple-math')
    # Iterate over each span tag and replace the value within the <sup> tag
    for span_tag in span_tags:
        sup_tag = span_tag.find('sup')
        if sup_tag == None:
            continue
        sup_text = sup_tag.get_text()
        sup_tag.contents[0].string.replace_with('')
        span_text = span_tag.contents[0].string
        span_text += f'^{sup_text}'
        span_tag.contents[0].string.replace_with(span_text)        
    return soup

# Extract all tables from html file provided in html form and extra footnotes for aanda journals
# Also replace sup tags with real values to display
def extract_html_tables(html_content):
    updated_soup = replace_sup_tags(html_content)
    tables = updated_soup.find_all('table')
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
    table_info = {}
    soup = BeautifulSoup(html_content, 'html.parser')

    notes_section = soup.find('div', class_='history')
    description_section = soup.find('div', id='annex')

    if notes_section == None:
        table_info['description'] = description_section.find(
            'p').get_text(strip=True)
        return table_info

    if description_section == None:
        return None

    table_info['description'] = description_section.find(
        'p').get_text(strip=True)
    table_info['notes'] = notes_section.find(
        'p').get_text(strip=True).replace('Notes.', '')

    return table_info

# Search journal metadata (authors, title, date, journal) and return a map with the values (in json format)
def search_aanda_metadata(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    metas = soup.find_all('meta')
    metadata = {}
    authors = []
    for meta in metas:
        content = meta.get('content')
        name = meta.get('name')
        match name:
            case 'citation_author':
                authors.append(content)
            case 'citation_journal_title':
                metadata['journal'] = content
            case 'citation_title':
                metadata['title'] = content
            case 'citation_publication_date':
                metadata['date'] = content
    metadata['author(s)'] = authors
    return metadata

# Extract aanda journal metadata
def extract_aanda_metadata(html_content):
    metadata = search_aanda_metadata(html_content)
    return metadata

# Validate footnotes found through initial parsing and returns only the correct ones
def validate_aanda_footnotes(footnotes, valid_footnotes, data_found):
    if not footnotes:
        return None

    for footnote in footnotes:
        footnote_constraint = '(' in footnote and ')' in footnote
        for data in data_found:
            if footnote in data and footnote_constraint:
                valid_footnotes[footnote] = footnotes[footnote]
    return valid_footnotes

# Search for footnote in entry and if found, add it to the json object the entry belongs to
def search_and_add_footnote_to_obj(footnotes, entry, json_obj):
    for footnote in footnotes:
        if footnote in entry:
            json_obj[footnote] = footnotes[footnote]

# Convert list of data extracted from table to json array
def convert_to_json_array(list, json_data, key_prefix, footnotes):
    json_objects = []
    counter = 1
    for entry in list:
        json_obj = {}
        json_obj[counter] = entry
        if footnotes:
            search_and_add_footnote_to_obj(footnotes, entry, json_obj)
        json_objects.append(json_obj)
        counter += 1
    json_data[key_prefix] = json_objects

# Add metadata and table info in json data for a table
def table_info_to_json_data(metadata, table_info, json_data):
    json_data['metadata'] = metadata
    json_data['table info'] = table_info

# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
# and then converted into json files
def extract_table_data(table, title, footnotes, metadata, table_info):
    json_data = {}
    table_info_to_json_data(metadata, table_info, json_data)

    key_prefix = f'headers'
    headers = list(th.get_text() for th in table.find("tr").find_all("th"))
    if len(headers) == 0:
        headers = list(td.get_text() for td in table.find("tr").find_all("td"))

    print(headers)
    convert_to_json_array(headers, json_data, key_prefix, None)

    valid_footnotes = {}
    for row in table.find_all("tr")[1:]:
        key_prefix = f'row{str(table.find_all("tr").index(row))}'
        data_found = list(td.get_text().replace('\xa0', EMPTY).replace(
            '\n', EMPTY) for td in row.find_all("td"))
        print(data_found)
        if 'A&A' in title:
            valid_footnotes = validate_aanda_footnotes(
                footnotes, valid_footnotes, data_found)
        convert_to_json_array(data_found, json_data,
                              key_prefix, valid_footnotes)
    write_to_json_file('json_results', title, json_data)
    return json_data

# Write json data to json file
# Title is the title of the json file
# Directory name is the directory the json file will be stored
def write_to_json_file(directory_name, title, json_data):
    create_directory(directory_name)
    path_to_json = os.path.join(directory_name, f'{title}.json')
    file = open(path_to_json, 'w', encoding='utf-8')
    file.write(json.dumps(json_data, indent=1))

# Upload index on elasticsearch
def append_json_index(actions, parent_index, doc_index_id, title, content):
    add_document_to_actions(actions, parent_index, doc_index_id, title, content)
    
# Search for metadata in initial aanda
# journal (without the tables)
def search_aanda_journal_metadata(journal):
    metadata = {}
    for aanda_file in list(title_to_metadata.keys()):
        if aanda_file.replace('.html', '') in journal:
            metadata = title_to_metadata[aanda_file]
    return metadata

# Extract all table data found in html files in given directory and print them
# If extra links for tables are included, these links are appended in links_to_extract
# and are handled after the simple ones
def extract_tables(directory_name):
    if os.path.exists(directory_name) == False:
        return
    parent_index = ''
    actions = []
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
   
        if 'A&A' in entry and 'A&A)_T' not in entry:
            title_to_metadata[entry] = extract_aanda_metadata(entry_content)
            continue
        
        tables = extract_html_tables(entry_content)
        parent_index = 'a&a'
        footnotes = search_aanda_footnotes(entry_content)
        table_info = search_aanda_table_info(entry_content)
        metadata = search_aanda_journal_metadata(entry)
        index_parent(parent_index, 1)
        for table in tables:
            json_data = extract_table_data(table, entry.replace(
                '.html', ''), footnotes, metadata, table_info)
            doc_index_id = os.listdir(directory_name).index(entry)
            append_json_index(actions, parent_index, doc_index_id, metadata['title'], json_data)
        upload_docs_to_index(parent_index, actions)
        
            