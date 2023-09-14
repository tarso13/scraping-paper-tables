from elasticsearch import Elasticsearch
import sys
sys.path.append('../')
from password import get_password

documents = []

def establish_connection_to_index():
    elastic_password = get_password('../elastic_password.txt')

    es = Elasticsearch(
        [{"host": "127.0.0.1", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password]
    )
    
    return es
    
# Read elastic password from file so as to keep it private  
# Create a connection to Elasticsearch
# Index the document which is the parent index
def index_parent(parent_index, parent_index_id):
    es = establish_connection_to_index()
   
    doc = {}
    
    indx = es.index(index=parent_index, id=parent_index_id, document=doc)
    print(indx)
    print('\n')

# Read elastic password from file so as to keep it private  
# Create a connection to Elasticsearch
# Update the parent index with new content
def add_document_to_index(parent_index, doc_index_id, content):
   es = establish_connection_to_index()
   es.index(index=parent_index, id=doc_index_id, body=content) 

# Read elastic password from file so as to keep it private  
# Create a connection to Elasticsearch
# Delete index given (for debugging purposes so far)
def delete_an_index(index):
    es = establish_connection_to_index()
    es.options(ignore_status=[400,404]).indices.delete(index=index)
    
def search_index_by_title(index, title):
    es = establish_connection_to_index()
    # define the search query
    query = {    
        'query': {        
            'match': {            
                'title' : title     
            }    
        }
    }

    # search for documents
    result = es.search(index=index, body=query)
    print(result)
    print('\n')
    
def search_index_by_content(index, content):
    es = establish_connection_to_index()
    
    # define the search query
    query = {    
        'query': {        
            'match': {            
                'content' : content     
            }    
        }
    }

    # search for documents
    result = es.search(index=index, body=query)
    print(result)
    print('\n')