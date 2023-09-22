import json
import re

# Map containing a table footnote as key and its content as value
mnras_footnotes = {}

# Identify metadata of the whole mnras journal using the script tag including
# specific data like date, authors and journal
def extract_mnras_extra_metadata(soup_content):
    script_tags = soup_content.find_all('script')
    for script_tag in script_tags:
        text = script_tag.get_text()
        if not text:
            continue
        if 'var dataLayer' in text:
            break

    json_match = re.search(r'\[{.*}\];', text)
    if json_match:
        json_data = json_match.group()

        json_data = json_data.replace(
            '[', '').replace(']', '',).replace(';', '')
        json_data = json.loads(json_data)
        date = json_data["online_publication_date"].replace('/', '-')
        journal = json_data["siteid"]
        authors_string = json_data["authors"]
        authors = authors_string.split(',')
        return date, journal, authors
    return None, None, None

# Search for footnote in MNRAs list of data and if found, add it to the json object the entry belongs to
def search_and_add_mnras_footnote_to_obj(footnotes, data, json_obj):
    for footnote in footnotes:
        if footnote in data:
            updated_data = data.replace(footnote, '')
            json_obj['content'] = updated_data
            json_obj['note'] = footnotes[footnote].replace(footnote, '').replace('Notes.', '').replace('Note.', '').strip()
    
            
            
# Identify table id in mnras journal
def identify_mnras_table_id(table):
    table_parent_element = table.parent.parent.parent
    table_id = table_parent_element.find(
        "span", {"class": "label title-label"}).get_text()
    table_id = table_id.replace('Table', '').replace('.', '').strip()
    return table_id

# Search for mnras table info and set footnotes for later use 
def search_mnras_table_info_and_footnotes(table):
    table_parent_element = table.parent.parent.parent
    
    caption = table_parent_element.find("div", {"class": "caption"}).get_text()
    table_info = {}
    table_info['caption'] = caption
    
    notes_elements = table_parent_element.find_all(
        "div", {"class": "table-wrap-foot"})
    
    if notes_elements:
        notes = ''
        for notes_element in notes_elements:
            note_text = notes_element.get_text()
            notes += note_text
            
            footnote_tags = notes_element.find_all("div", {"class": "footnote"})
            if footnote_tags:
                for footnote_tag in footnote_tags:
                    span_tag = footnote_tag.find("span")
                    sup_tags = span_tag.find_all("sup")
                    if not sup_tags:
                        continue
                    for sup_tag in sup_tags:
                        footnote = sup_tag.get_text()
                        footnote_content = span_tag.find(
                            "p", {"class": "chapter-para"}).get_text()
                        mnras_footnotes[footnote] = footnote_content
        table_info['notes'] = notes.replace('Notes.', '').replace('Note.', '')
    return table_info
