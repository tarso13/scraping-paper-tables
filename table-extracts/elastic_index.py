from elasticsearch import Elasticsearch
import sys

sys.path.append("../")
from password import get_password
import datetime as dt

documents = []

minimum_results = 0


# Read elastic password from file so as to keep it private
# Create a connection to Elasticsearch
def establish_connection_to_index():
    elastic_password = get_password("../elastic_password.txt")

    es = Elasticsearch(
        [{"host": "localhost", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password],
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
    document_exists = es.exists(index=parent_index, id=doc_index_id)
    if document_exists:
        return -1
    es.index(index=parent_index, id=doc_index_id, body=content)
    return 0


# Create a connection to Elasticsearch
# Delete index given (for debugging purposes so far)
def delete_an_index(index):
    es = establish_connection_to_index()
    es.options(ignore_status=[400, 404]).indices.delete(index=index)


# Create a connection to Elasticsearch
# Search documents by title
def search_index_by_title(title, maximum_results=2000):
    es = establish_connection_to_index()

    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {"match_phrase": {"metadata.paper_title": title}},
    }

    results = es.search(body=query)
    if results["hits"]["total"]["value"] == 0:
        return "No results."
    total_hits = len(results["hits"]["hits"])
    journals_str = ""
    for i in range(0, total_hits):
        journals_str += str(results["hits"]["hits"][i]["_source"])
    return journals_str


# Search documents by word in their content
def search_index_by_word_in_table(parent_index, word, maximum_results=2000):
    es = establish_connection_to_index()

    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {"simple_query_string": {"query": word}},
    }

    try:
        results = es.search(index=parent_index, body=query)
    except:
        return "Try another word/phrase. It is likely that there are too many matches."

    if results["hits"]["total"]["value"] == 0:
        return "No results."
    total_hits = len(results["hits"]["hits"])
    journals_str = ""
    for i in range(0, total_hits):
        journals_str += str(results["hits"]["hits"][i]["_source"])
    return journals_str


# Create a connection to Elasticsearch
# Search documents by brief notes on table caption
def search_index_by_table_caption(content, maximum_results=2000):
    es = establish_connection_to_index()

    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {"match": {"table_info.caption": content}},
    }

    results = es.search(body=query)
    if results["hits"]["total"]["value"] == 0:
        return "No results."
    total_hits = len(results["hits"]["hits"])
    journals_str = ""
    for i in range(0, total_hits):
        journals_str += str(results["hits"]["hits"][i]["_source"])
    return journals_str


# Create a connection to Elasticsearch
# Search documents by date range
# The journals returned have publication date greater or equal to start_date given
# and less or equal to end_date given
# Note: Date should be either in yyyy-mm-dd or yyyy/mm/dd format
def search_index_by_date(start_date, end_date, maximum_results=2000):
    es = establish_connection_to_index()

    formatted_start_date = format_date(start_date)
    formatted_end_date = format_date(end_date)

    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {
            "range": {
                "metadata.date": {
                    "gte": formatted_start_date,
                    "lte": formatted_end_date,
                }
            }
        },
    }

    results = es.search(body=query)
    if results["hits"]["total"]["value"] == 0:
        return "No results."
    total_hits = len(results["hits"]["hits"])
    journals_str = ""
    for i in range(0, total_hits):
        journals_str += str(results["hits"]["hits"][i]["_source"])
    return journals_str


# Create a connection to Elasticsearch
# Search documents by year
def search_index_by_year(year, maximum_results=2000):
    start_date = format_date(f"{str(year)}-01-01")
    end_date = format_date(f"{str(year)}-12-31")
    return search_index_by_date(start_date, end_date, maximum_results)


# Create a connection to Elasticsearch
# Search documents by year range
def search_index_by_year_range(start_year, end_year, maximum_results=2000):
    start_date = format_date(f"{str(start_year)}-01-01")
    end_date = format_date(f"{str(end_year)}-12-31")
    return search_index_by_date(start_date, end_date, maximum_results)


# Create a connection to Elasticsearch
# Search documents by journal name
def search_index_by_journal(journal, maximum_results=2000):
    es = establish_connection_to_index()

    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {"match_phrase": {"metadata.journal": journal}},
    }

    results = es.search(body=query)
    if results["hits"]["total"]["value"] == 0:
        return "No results."
    total_hits = len(results["hits"]["hits"])
    journals_str = ""
    for i in range(0, total_hits):
        journals_str += str(results["hits"]["hits"][i]["_source"])
    return journals_str


# Create a connection to Elasticsearch
# Search documents by author name
def search_index_by_author(author, maximum_results=2000):
    es = establish_connection_to_index()

    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {"match": {"metadata.author(s)": author}},
    }

    results = es.search(body=query)
    if results["hits"]["total"]["value"] == 0:
        return "No results."
    total_hits = len(results["hits"]["hits"])
    journals_str = ""
    for i in range(0, total_hits):
        journals_str += str(results["hits"]["hits"][i]["_source"])
    return journals_str


# Format date in order to guarantee its type in elastic document
def format_date(date):
    d = dt.datetime.strptime(str(date).replace("/", "-"), "%Y-%m-%d")
    d = d.date()
    return d.isoformat()
