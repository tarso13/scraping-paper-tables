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

# Include '^' in sup tags text indicating power exponentiation
def replace_sup_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
  
    sup_tags = soup.find_all('sup')
    if sup_tags == None:
        return
    for sup_tag in sup_tags:
        sup_text = sup_tag.get_text()
        sup_tag.contents[0].string.replace_with(f'^{sup_text}')
         
    return soup

# Include '_' in sub tags text indicating subscripts
def replace_sub_tags(soup):
    sub_tags = soup.find_all('sub')
    if sub_tags == None:
        return
    for sub_tag in sub_tags:
        sub_text = sub_tag.get_text()
        if sub_tag.contents[0].string == None:
            sub_tag.contents[0].string = ''
        sub_tag.contents[0].string.replace_with(f'_{sub_text}')
         
    return soup

# Extract all tables from html file provided in html form and extra footnotes for aanda journals
# Also replace sup and sub tags representing actual values 
def extract_html_tables(html_content):
    updated_soup = replace_sup_tags(html_content)
    re_updated_soup = replace_sub_tags(updated_soup)
    tables = re_updated_soup.find_all('table')
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
        table_info['context'] = description_section.find(
            'p').get_text(strip=True)
        return table_info

    if description_section == None:
        return None

    table_info['context'] = description_section.find(
        'p').get_text(strip=True)
    table_info['notes'] = notes_section.find(
        'p').get_text(strip=True)

    return table_info

# Search journal metadata (authors, title, date, journal) and return a map with the values (in json format)
def search_metadata(html_content):
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
def extract_journal_metadata(html_content):
    metadata = search_metadata(html_content)
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

# Search for footnote in aanda entry and if found, add it to the json object the entry belongs to
def search_and_add_aanda_footnote_to_obj(footnotes, entry, json_obj):
    for footnote in footnotes:
        if footnote in entry:
            json_obj['content'] = json_obj['content'].replace(f'^{str(footnote)}', '')
            json_obj['note'] = footnotes[footnote]

# Search for footnote in IOPscience list of data and if found, add it to the json object the entry belongs to
def search_and_add_iopscience_footnote_to_obj(footnotes, data, json_obj):
    for footnote in footnotes:
        index = footnotes.index(footnote)
        for key in footnote.keys():
            if f'^{key}' in data:
                json_obj['content'] = json_obj['content'].replace(f'^{str(key)}', '')
                note = footnotes[index]
                note[key] = note[key].replace('Note. ', '')
                position = note[key].find(key)
                json_obj['note'] = note[key][position + 1:len(note[key])]
                footnotes.remove(footnote)
                    
# Convert list of data extracted from table to json array
def convert_to_json_array(list, json_data, key_prefix, footnotes, journal):
    json_objects = []
    counter = 1
    for entry in list:
        json_obj = {}
        json_obj[counter] = {'content' : entry}
        if journal == 'A&A' and footnotes:
            search_and_add_aanda_footnote_to_obj(footnotes, entry, json_obj[counter])
        if journal == 'IOPscience' and footnotes:
            search_and_add_iopscience_footnote_to_obj(footnotes, entry, json_obj[counter])
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
def extract_table_data(table, title, footnotes, metadata, table_info, table_number):
    json_data = {}
    
    current_table_info = {}
    if 'A&A' in title:
        current_table_info = table_info
        
    if 'IOPscience' in title:
        current_table_info['context'] = table_info['context'][table_number]
        current_table_info['notes'] = table_info['notes'][table_number]
        if current_table_info['notes'] == '':
            current_table_info.pop('notes')
        
    table_info_to_json_data(metadata, current_table_info, json_data)

    key_prefix = f'headers'
    headers = []
    extra_headers = []
    
    counter = 0
    key_prefix = f'headers'
    for tr in table.find_all("tr"):
        counter += 1
        for th in tr.find_all("th"):
            if counter > 1:
                extra_headers.append(th.get_text().replace('\xa0', EMPTY).replace('\n', ''))
                continue
            headers.append(th.get_text().replace('\xa0', EMPTY).replace('\n', ''))

    if len(headers) == 0:
        headers = list(td.get_text() for td in table.find("tr").find_all("td"))

    print(headers)
    print('Extra headers: ' + str(extra_headers))
    
    if 'IOPscience' in title:
        convert_to_json_array(headers, json_data, key_prefix, footnotes, 'IOPscience')
        if len(extra_headers) != 0:
            key_prefix = f'extra_{key_prefix}'
            convert_to_json_array(extra_headers, json_data, key_prefix, None, 'IOPscience')
    else:
        convert_to_json_array(headers, json_data, key_prefix, None, 'A&A')
        
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
                           key_prefix, valid_footnotes, 'A&A')
      
            
    write_to_json_file('json_results', f'{title}', json_data)
    return json_data

# Write json data to json file
# Title is the title of the json file
# Directory name is the directory the json file will be stored
def write_to_json_file(directory_name, title, json_data):
    create_directory(directory_name)
    path_to_json = os.path.join(directory_name, f'{title}.json')
    file = open(path_to_json, 'w', encoding='utf-8')
    file.write(json.dumps(json_data, indent = 1))

# Append document to actions in order to update the parent elastic index
def append_to_elastic_index(actions, parent_index, doc_index_id, title, content):
    add_document_to_actions(actions, parent_index, doc_index_id, title, content)
    
# Search for metadata in initial aanda
# journal (without the tables)
def search_aanda_journal_metadata(journal):
    metadata = {}
    for aanda_file in list(title_to_metadata.keys()):
        if aanda_file.replace('.html', '') in journal:
            metadata = title_to_metadata[aanda_file]
    return metadata

# Search for footnotes in iopscience journal
def search_iopscience_footnotes(journal, table_info):
    soup = BeautifulSoup(journal, 'html.parser')
  
    small_tags = soup.find_all('small')
    if small_tags == None:
        return
    
    footnotes = []
    for small_tag in small_tags:
        sup_tag = small_tag.find('sup')
        if sup_tag == None:
            continue
        sup_text = sup_tag.get_text().replace(' ', '').replace('\n', '')
        if sup_text == None:
            continue
        if sup_text.isalpha():
            footnote_value = small_tag.get_text().replace('\n', '')
            footnotes.append({sup_text : footnote_value})
            if footnote_value in table_info['notes']:
                index = table_info['notes'].index(footnote_value)
                table_info['notes'][index] = ''
           
    return footnotes

# Search for table notes in iopscience journal
def search_iopscience_table_notes(journal):
    soup = BeautifulSoup(journal, 'html.parser')
    p_tags = soup.find_all('p')
    notes = []
    for p_tag in p_tags:
        small_tag = p_tag.find('small')
        if small_tag == None:
            continue
        strong_tag = small_tag.find('strong')
        if strong_tag == None:
            continue 
        notes.append(small_tag.get_text().replace('\n', ''))
    return notes

# Search for table contexts in iopscience journal
def search_iopscience_table_contexts(journal):
    soup = BeautifulSoup(journal, 'html.parser')
    p_tags = soup.find_all('p')
    contexts = []
    for p_tag in p_tags:
        b_tag = p_tag.find('b')
        if b_tag == None:
            continue
        if 'Table' not in b_tag.get_text():
            continue
        p_text = p_tag.get_text().replace(b_tag.get_text(), '').replace('\xa0', EMPTY)
        contexts.append(p_text)
    return contexts

# Search for table info in iopscience journal, including notes and context
def search_iopscience_table_info(journal):
    table_info = {}
    table_info['notes'] = search_iopscience_table_notes(journal)
    table_info['context'] = search_iopscience_table_contexts(journal)
    return table_info

# Extract all table data found in html files in given directory and print them
# If extra links for tables are included, these links are appended in links_to_extract
# and are handled after the simple ones
def extract_tables(directory_name):
    if os.path.exists(directory_name) == False:
        return
    parent_index = ''
    actions = []
    iopscience_counter = 0
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
            title_to_metadata[entry] = extract_journal_metadata(entry_content)
            continue
        
        tables = extract_html_tables(entry_content)
        parent_index = ''
        parent_index_id = 0
        footnotes = {}
        metadata = {}
        table_info = {}
        
        if 'A&A' in entry:
            parent_index = 'a&a'
            parent_index_id = 0
            footnotes =  search_aanda_footnotes(entry_content)
            table_info = search_aanda_table_info(entry_content)
            metadata = search_aanda_journal_metadata(entry)
         
        if 'IOPscience' in entry:
            parent_index = 'iopscience'
            parent_index_id = 1
            table_info = search_iopscience_table_info(entry_content)
            footnotes =  search_iopscience_footnotes(entry_content, table_info)
            metadata = extract_journal_metadata(entry_content)
            
        index_parent(parent_index, parent_index_id)

        for table in tables:
            doc_index_id = 0
            title = entry.replace('.html', '')
            index = tables.index(table)
            if 'IOPscience' in title:
                title += f'_T{str(index + 1)}'
                doc_index_id = index
            
            if 'A&A' in title:
                doc_index_id = os.listdir(directory_name).index(entry) + 1
            
            json_data = extract_table_data(table, title, footnotes, metadata, table_info, index)
            append_to_elastic_index(actions, parent_index, doc_index_id, title.replace('_', ' '), json_data)
        upload_new_index(parent_index, actions)