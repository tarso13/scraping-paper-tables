from elasticsearch import Elasticsearch
import sys
sys.path.append('../')
from password import get_password

def upload_index(index_id, title, content):
    # Read elastic password from file so as to keep it private  
    elastic_password = get_password('../elastic_password.txt')

    # Create a connection to Elasticsearch
    es = Elasticsearch(
        [{"host": "127.0.0.1", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password],
    )

    # Define the document data
    doc = {
        "title": title,
        "content": content,
    }

    # Index the document
    indx = es.index(index=title, id=index_id, document=doc)
    print(indx)
    print('\n')