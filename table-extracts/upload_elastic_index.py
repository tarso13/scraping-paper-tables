from elasticsearch import Elasticsearch
import sys
sys.path.append('../')
from password import get_password

def index_parent(parent_index, parent_index_id):
    # Read elastic password from file so as to keep it private  
    elastic_password = get_password('../elastic_password.txt')

    # Create a connection to Elasticsearch
    es = Elasticsearch(
        [{"host": "127.0.0.1", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password],
    )
    doc = {}
    # Index the document
    indx = es.index(index=parent_index, id=parent_index_id, document=doc)
    print(indx)
    print('\n')

def add_document_to_actions(actions, parent_index, doc_index_id, title, content):
    action = {"index": {"_index": parent_index, "_id": doc_index_id}}
    # Define the document data
    doc = {
        "title": title,
        "content": content,
    }
    actions.append(action)
    actions.append(doc)

def upload_docs_to_index(parent_index, actions):
    # Read elastic password from file so as to keep it private  
    elastic_password = get_password('../elastic_password.txt')

    # Create a connection to Elasticsearch
    es = Elasticsearch(
        [{"host": "127.0.0.1", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password],
    )
    
    es.bulk(index=parent_index, operations=actions)