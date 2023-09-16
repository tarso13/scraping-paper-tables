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
    
    indx = es.index(index=parent_index, id=parent_index_id, document=doc)
    print(indx)
    print('\n')

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
                'title' : title     
            }    
        }
    }

    result = es.search(index=index, body=query)
    print(result)
    print('\n')
   
# Create a connection to Elasticsearch  
# Search documents by content
def search_index_by_content(index, content):
    es = establish_connection_to_index()
    
    query = {    
        'query': {        
            'match': {            
                'content' : content     
            }    
        }
    }

    result = es.search(index=index, body=query)
    print(result)
    print('\n')

# Create a connection to Elasticsearch
# Search documents by content
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
    
def format_date(date):
    d = dt.datetime.strptime(str(date).replace('/', '-'), "%Y-%m-%d")
    d = d.date()
    return d.isoformat()