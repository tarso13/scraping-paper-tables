from bs4 import BeautifulSoup
import json
import re

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
        journal = json_data["supplier_tag"]
        authors = [json_data["authors"]]
        return date, journal, authors
    return None, None, None