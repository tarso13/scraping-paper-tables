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

    # Extract the (a), (b), (c) labels and their text
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
        'p').get_text(strip=True)

    return table_info

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
            json_obj['content'] = json_obj['content'].replace(f'{str(footnote)}', '')
            json_obj['note'] = footnotes[footnote]

# Search for metadata in initial aanda
# journal (without table suffix)
def search_aanda_journal_metadata(journal):
    metadata = {}
    for aanda_file in list(title_to_metadata.keys()):
        if aanda_file.replace('.html', '') in journal:
            metadata = title_to_metadata[aanda_file]
    return metadata