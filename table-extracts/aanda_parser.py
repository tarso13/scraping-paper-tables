# Value used to replace undesired word occurences in datasets
EMPTY = ''

# Map containing the initial aanda title as key with its metadata as value
title_to_metadata = {}

# Search for footnotes in aanda articles
def search_aanda_footnotes(soup_content):
    notes_section = soup_content.find('div', class_='history')

    if notes_section == None:
        return None

    labels = notes_section.find_all('sup')
    footnotes_kvs = {}

    for label in labels:
        label_name = label.get_text(strip=True)
        label_text = label.find_next('p').get_text(strip=True)
        footnotes_kvs[label_name] = label_text
    return footnotes_kvs

# Search and extract table description and notes
def search_aanda_table_info(soup_content):
    table_info = {}
    
    notes_section = soup_content.find('div', class_='history')
    description_section = soup_content.find('div', id='annex')

    if notes_section == None:
        table_info['caption'] = description_section.find(
            'p').get_text(strip=True)
        return table_info

    if description_section == None:
        return None

    table_info['caption'] = description_section.find(
        'p').get_text(strip=True)
    table_info['notes'] = notes_section.find(
        'p').get_text(strip=True).replace('Notes.', '')
    
    if table_info['notes'] == '':
        notes_text = ''
        notes = notes_section.find_all('div')
        for note in notes:
            notes_text += note.get_text()
        table_info['notes'] = notes_text
        
    return table_info

# Validate footnotes found through initial parsing and returns only the correct ones
def validate_aanda_footnotes(footnotes, valid_footnotes, data_found):
    if not footnotes:
        return None

    for footnote in footnotes:
        footnote_constraint = '(' in footnote and ')' in footnote
        value = footnote.replace('(', '').replace(')', '').replace('^', '')
        int_footnote = value.isnumeric()
        positive_footnote = int_footnote and int(value) > 0
        valid_footnote = footnote_constraint or positive_footnote
        for data in data_found:
            if not valid_footnote:
                continue
            if footnote in data or f'^{value}' in data:
                valid_footnotes[footnote] = footnotes[footnote]
    return valid_footnotes

# Search for footnote in aanda entry and if found, add it to the json object the entry belongs to
def search_and_add_aanda_footnote_to_obj(footnotes, entry, json_obj):
    for footnote in footnotes:
        possible_footnote_value = footnote.replace('(','').replace(')', '')
        if footnote in entry:
            json_obj['content'] = json_obj['content'].replace(f'{str(footnote)}', '')
            json_obj['note'] = footnotes[footnote]
            continue
        if possible_footnote_value in entry:
            json_obj['content'] = json_obj['content'].replace(f'{possible_footnote_value}', '')
            json_obj['note'] = footnotes[footnote]
        
        
# Search for metadata in initial aanda
# journal (without table suffix)
def search_aanda_journal_metadata(journal):
    metadata = {}
    for aanda_file in list(title_to_metadata.keys()):
        if aanda_file.replace('.html', '') in journal:
            metadata = title_to_metadata[aanda_file]
    return metadata