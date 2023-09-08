from bs4 import BeautifulSoup
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
    
        json_data = json_data.replace('[', '').replace(']', '',).replace(';', '')
        json_data = json.loads(json_data)
        date = json_data["online_publication_date"]
        journal = json_data["siteid"]
        authors = [json_data["authors"]]
        return date, journal, authors
    return None, None, None

# Search for footnote in MNRAs list of data and if found, add it to the json object the entry belongs to
def search_and_add_mnras_footnote_to_obj(footnotes, data, json_obj):
    for footnote in footnotes:
        if footnote in data:
            updated_data = data.replace(footnote, '')
            json_obj['content'] = updated_data
            json_obj['note'] = footnotes[footnote].replace(footnote, '')
               
          