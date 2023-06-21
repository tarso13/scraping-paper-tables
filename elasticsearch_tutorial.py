from elasticsearch import Elasticsearch
from elastic_password import get_elastic_password

# Read elastic password from file so as to keep it private  
elastic_password = get_elastic_password('elastic_password.txt')

# Create a connection to Elasticsearch
es = Elasticsearch(
    [{"host": "localhost", "port": 9200, "scheme": "http"}],
    basic_auth=["elastic", elastic_password],
)

# Define the document data
doc = {
    "title": "Elasticsearch tutorial",
    "content": "This is an attempt to use elasticsearch in python.",
}

# Index the document
indx = es.index(index='my_index', id=1, document=doc)
print(indx)
print('\n')

# Define the search query and search for document
search_result = es.search(index='my_index', query = {"match": {"content": "elasticsearch"}})
print(search_result)
print('\n')

# Update the document content
update_doc = es.update(index='my_index', id=1, doc= {"content": "This is an attempt to update the content of the document."})
print(update_doc)
print('\n')

# Define the search query in search (new syntax) and search for the updated document
search_result = es.search(index='my_index', query = {"match": {"content": "update"}})
print(search_result)
