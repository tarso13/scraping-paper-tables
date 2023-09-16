from elasticsearch import Elasticsearch
import sys
sys.path.append('../')
from password import get_password
import datetime as dt

documents = []

# Read elastic password from file so as to keep it private  
# Create a connection to Elasticsearch
def establish_connection_to_index():
    elastic_password = get_password('../elastic_password.txt')

    es = Elasticsearch(
        [{"host": "127.0.0.1", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password]
    )
    
    return es
    
# Create a connection to Elasticsearch
# Index the document which is the parent index
def index_parent(parent_index, parent_index_id):
    es = establish_connection_to_index()
   
    doc = {}
    
    es.index(index=parent_index, id=parent_index_id, document=doc)


# Create a connection to Elasticsearch
# Update the parent index with new content
def add_document_to_index(parent_index, doc_index_id, content):
   es = establish_connection_to_index()
   es.index(index=parent_index, id=doc_index_id, body=content) 

# Create a connection to Elasticsearch
# Delete index given (for debugging purposes so far)
def delete_an_index(index):
    es = establish_connection_to_index()
    es.options(ignore_status=[400,404]).indices.delete(index=index)
    
# Create a connection to Elasticsearch
# Search documents by title
def search_index_by_title(index, title):
    es = establish_connection_to_index()
    
    query = {    
        'query': {        
            'match': {            
                'metadata.title' : title     
            }    
        }
    }

    results = es.search(index=index, body=query)
    return results
   
# Create a connection to Elasticsearch  
# Search documents by brief notes on table caption
def search_index_by_table_caption(index, content):
    es = establish_connection_to_index()
    
    query = {    
        'query': {        
            'match': {    
                    'table info.caption' : content           
            }    
        }
    }

    results = es.search(index=index, body=query)
    return results

# Create a connection to Elasticsearch
# Search documents by date range
# The journals returned have publication date greater or equal to start_date given
# and less or equal to end_date given
# Note: Date should be either in yyyy-mm-dd or yyyy/mm/dd format
def search_index_by_date(index, start_date, end_date):
    es = establish_connection_to_index()
    
    formatted_start_date = format_date(start_date)
    formatted_end_date = format_date(end_date)
    
    query = {    
        'query': {        
            'range': {
                'metadata.date':{
                        'gte': formatted_start_date,
                        'lte': formatted_end_date
                }
            }
        }
    }

    results = es.search(index=index, body=query)
    return results

# Create a connection to Elasticsearch
# Search documents by journal name
# It is based on similarity of the given journal
# name and the ones existent on index
# e.g. 'The Astronomical Journal' returns both
# 'The Astrophysical Journal' and 'The Astrophysical Journal' journals,
# whereas 'Astronomical' returns only 'The Astrophysical Journal' journals
def search_index_by_journal(index, journal):
    es = establish_connection_to_index()
    
    query = {    
        'query': {        
            'match': {
                'metadata.journal' : journal
                }
            }
        }

    results = es.search(index=index, body=query)
    return results

# Create a connection to Elasticsearch
# Search documents by author name
def search_index_by_author(index, author):
    es = establish_connection_to_index()
    
    query = {    
        'query': {        
            'match': {
                'metadata.author(s)' : author
                }
            }
        }

    results = es.search(index=index, body=query)
    print(results)
    return results

# Format date in order to guarantee its type in elastic document
def format_date(date):
    d = dt.datetime.strptime(str(date).replace('/', '-'), "%Y-%m-%d")
    d = d.date()
    return d.isoformat()