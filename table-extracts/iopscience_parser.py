# Value used to replace undesired word occurences in datasets
EMPTY = ''

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

# Search for footnotes in iopscience journal
def search_iopscience_footnotes(soup_content, table_info):
  
    small_tags = soup_content.find_all('small')
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
def search_iopscience_table_notes(soup_content):
    p_tags = soup_content.find_all('p')
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
def search_iopscience_table_contexts(soup_content):
    p_tags = soup_content.find_all('p')
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
def search_iopscience_table_info(soup_content):
    table_info = {}
    table_info['notes'] = search_iopscience_table_notes(soup_content)
    table_info['context'] = search_iopscience_table_contexts(soup_content)
    return table_info
