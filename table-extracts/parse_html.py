from bs4 import BeautifulSoup
import os
import json
from upload_elastic_index import *
from aanda_parser import *
from iopscience_parser import *

doc_index_id = 0 

# List containing the html files with tables that have been extracted
files_extracted = []

# Map containing the (extra) url as key and the table suffix as value
url_suffixes = {}

# Get file content
def get_file_content(filepath):
    file = open(filepath, "r", encoding="utf-8")
    content = file.read()
    file.close()
    return content

# Include '^' in sup tags text indicating power exponentiation
def replace_sup_tags(soup_content):
    sup_tags = soup_content.find_all('sup')
    if sup_tags == None:
        return
    for sup_tag in sup_tags:
        sup_text = sup_tag.get_text()
        sup_tag.contents[0].string.replace_with(f'^{sup_text}')
         
    return soup_content

# Include '_' in sub tags text indicating subscripts
def replace_sub_tags(soup_content):
    sub_tags = soup_content.find_all('sub')
    if sub_tags == None:
        return
    for sub_tag in sub_tags:
        sub_text = sub_tag.get_text()
        sub_tag.contents[0].string.replace_with(f'_{sub_text}')
         
    return soup_content

# Extract all tables from html file provided in html form and extra footnotes for journals
# Also replace sup and sub tags representing actual values 
def extract_html_tables(soup_content):
    updated_soup = replace_sup_tags(soup_content)
    re_updated_soup = replace_sub_tags(updated_soup)
    tables = re_updated_soup.find_all('table')
    return tables


# Search journal metadata (authors, title, date, journal) and return a map with the values (in json format)
def search_metadata(soup_content):
    metas = soup_content.find_all('meta')
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
def extract_journal_metadata(soup_content):
    metadata = search_metadata(soup_content)
    return metadata

# Convert and add footnote to json object depending on journal
def footnote_to_json_object(journal, footnotes, entry, json_obj, key_prefix):
    if journal == 'A&A':
        search_and_add_aanda_footnote_to_obj(footnotes, entry, json_obj)
    if journal == 'IOPscience':
        search_and_add_iopscience_footnote_to_obj(footnotes, entry, json_obj, key_prefix)
        
# Convert list of data extracted from table to json array
def convert_to_json_array(list, json_data, key_prefix, footnotes, journal, header):
    if len(list) == 0:
        return
    json_objects = []
    counter = 1
    for entry in list:
        json_obj = {}
        index = f'col{str(counter)}'    
        json_obj[index] = {'content' : entry}
        if header == True:
            json_obj[index]['header'] = 'true'
        if footnotes:
            footnote_to_json_object(journal, footnotes, entry, json_obj[index], key_prefix)
        json_objects.append(json_obj)
        counter += 1
    json_data[key_prefix] = json_objects

# Add metadata and table info in json data for a table
def table_info_to_json_data(metadata, table_info, json_data):
    json_data['metadata'] = metadata
    json_data['table info'] = table_info

def include_extra_metadata_json_data(extra_metadata, metadata, json_data):
    for key in extra_metadata:
        metadata[key] = extra_metadata[key]
    json_data['metadata'] = metadata

# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
# and then converted into json files
def extract_table_data(table, title, footnotes, metadata, extra_metadata,table_info, table_number):
    json_data = {}
    current_table_info = {}
    if 'A&A' in title:
        current_table_info = table_info
    
    if 'IOPscience' in title:
        current_table_info['caption'] = table_info['caption'][table_number]
        current_table_info['notes'] = table_info['notes'][table_number]
        if current_table_info['notes'] == '':
            current_table_info.pop('notes')
    
    metadata['title'] = title.replace('_',  ' ')
 
    key_prefix = f'row'
    headers = []
    extra_headers = []
    
    counter = 0
    for tr in table.find_all("tr"):
        counter += 1
        for th in tr.find_all("th"):   
            if counter > 1:
                extra_headers.append(th.get_text().replace('\xa0', EMPTY).replace('\n', ''))
                continue
            headers.append(th.get_text().replace('\xa0', EMPTY).replace('\n', '').replace('  ',''))
    
    key_prefix = f'row1'
    # print(headers)
    table_info_to_json_data(metadata, current_table_info, json_data)
    
    extra_metadata['headers'] = headers
    extra_metadata['rows'] = 0
    extra_metadata['cols'] = len(headers)
    
    if 'IOPscience' in title:
        convert_to_json_array(headers, json_data, key_prefix, footnotes, 'IOPscience', True)
        if len(extra_headers) != 0:
            # print(extra_headers)
            key_prefix = f'row2'
            convert_to_json_array(extra_headers, json_data, key_prefix, None, 'IOPscience', True)
    else:
        key_prefix = f'row1'
        convert_to_json_array(headers, json_data, key_prefix, None, 'A&A', True)
    
    valid_footnotes = {}
    header_count = 0
    if headers:
        header_count = key_prefix[len(key_prefix) - 1]
        
    table_rows = table.find_all("tr")
    for row in table_rows[1:]:
        row_index = table_rows.index(row)
        index = int(header_count) + row_index 
        key_prefix = f'row{str(index)}'
        data_found = list(td.get_text().replace('\xa0', EMPTY).replace(
            '\n', EMPTY).replace('  ','') for td in row.find_all("td"))
      
        if row_index == 1:
            extra_metadata['rows'] = len(table_rows)
            if not len(headers):    
                extra_metadata['cols'] = len(data_found)
            include_extra_metadata_json_data(extra_metadata, metadata, json_data)
        
        domain = ''
        # print(data_found)
        if 'A&A' in title:
            valid_footnotes = validate_aanda_footnotes(
                footnotes, valid_footnotes, data_found)
            domain = 'A&A'
        if 'IOPscience' in title:
            valid_footnotes = footnotes
            domain = 'IOPscience'
        convert_to_json_array(data_found, json_data,
                           key_prefix, valid_footnotes, domain, False)
      
 
    write_to_json_file('json_results', f'{title}', json_data)
    return json_data

# Write json data to json file
# Title is the title of the json file
# Directory name is the directory the json file will be stored
def write_to_json_file(directory_name, title, json_data):
    if not os.path.isdir(directory_name):
        os.mkdir(directory_name)
    path_to_json = os.path.join(directory_name, f'{title}.json')
    file = open(path_to_json, 'w', encoding='utf-8')
    file.write(json.dumps(json_data, indent = 1))

# Append document to actions in order to update the parent elastic index
def append_to_elastic_index(actions, parent_index, doc_index_id, title, content):
    add_document_to_actions(actions, parent_index, doc_index_id, title, content)
    
# Extract all table data found in html files in given directory and print them
def extract_downloaded_tables(directory_name):
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
   
        soup_content = BeautifulSoup(entry_content, 'html.parser')
        
        if 'A&A' in entry and 'A&A)_T' not in entry:
            title_to_metadata[entry] = extract_journal_metadata(soup_content)
            continue
        
        tables = extract_html_tables(soup_content)
        
        parent_index = 'astrophysics'
        parent_index_id = 0
        footnotes = None
        metadata = {}
        extra_metadata = {}
        table_info = {}
        
        if 'Captcha' in entry:
            continue
        
        if 'A&A' in entry:
            footnotes =  search_aanda_footnotes(soup_content)
            table_info = search_aanda_table_info(soup_content)
            metadata = search_aanda_journal_metadata(entry)

        if 'IOPscience' in entry:
            mrt_indexes = {}
            table_info = search_iopscience_table_info(soup_content)
            footnotes =  search_iopscience_footnotes(soup_content, table_info)
            metadata = extract_journal_metadata(soup_content)
            mrt_titles, json_results = extract_iopscience_mrt_tables(soup_content, 'iopscience_mrts')
            for result in json_results:
                index = json_results.index(result)
                mrt_title = mrt_titles[index]
                write_to_json_file('json_mrts', mrt_title, result)
                mrt_indexes[mrt_title] = result
                
        parent_index_id = 1   
        index_parent(parent_index, parent_index_id)

        for table in tables:
            title = entry.replace('.html', '')
            index = tables.index(table)
            if 'IOPscience' in title:
                title += f'_T{str(index + 1)}'
                
            global doc_index_id 
            doc_index_id += 1

            json_data = extract_table_data(table, title, footnotes, metadata, extra_metadata, table_info, index)
            append_to_elastic_index(actions, parent_index, doc_index_id, title.replace('_', ' '), json_data)
        
        for mrt_index in mrt_indexes:
            doc_index_id += 1
            append_to_elastic_index(actions, parent_index, doc_index_id, mrt_index, mrt_indexes[mrt_index])
        
        upload_new_index(parent_index, actions)