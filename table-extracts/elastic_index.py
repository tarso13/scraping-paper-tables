from elasticsearch import Elasticsearch
import sys
import json

sys.path.append("../")
from password import get_password
import datetime as dt

documents = []

minimum_results = 0


# Adjust journal name based on the journal name the user has provided
# Mostly useful for api use
def adjust_journal_name(journal_name):
    possible_mnras = [
        "MNRAS",
        "mnras",
        "Monthly Notices of the Royal Astronomical Society",
    ]

    possible_aanda = ["A&A", "a&a", "Astronomy & Astrophysics"]

    if journal_name in possible_mnras:
        return "mnras"

    if journal_name in possible_aanda:
        return "Astronomy & Astrophysics"

    return journal_name


# Check if table id exists in query results
def same_table_id_found(query_results, table_id):
    query_array = f"[{query_results}]"
    json_array = json.loads(query_array)
    for json_obj in json_array:
        metadata = json_obj.get("metadata", {})
        if metadata["table_id"] == table_id:
            return True
    return False


# Gets next available document id to append to index
def get_next_document_id(index):
    elastic_password = get_password("../elastic_password.txt")

    es = Elasticsearch(
        [{"host": "localhost", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password],
    )

    refresh_index(index)
    result = es.count(index=index)
    count = result["count"]
    return count + 1


# Read elastic password from file so as to keep it private
# Create a connection to Elasticsearch
def establish_connection_to_index():
    elastic_password = get_password("../elastic_password.txt")

    es = Elasticsearch(
        [{"host": "localhost", "port": 9200, "scheme": "http"}],
        basic_auth=["elastic", elastic_password],
    )

    return es


def collect_search_results(results):
    if results["hits"]["total"]["value"] == 0:
        return "No results."
    total_hits = len(results["hits"]["hits"])
    journals_str = ""
    for i in range(0, total_hits):
        obj = results["hits"]["hits"][i]["_source"]
        json_formatted_str = json.dumps(obj, indent=4)
        if i != 0:
            journals_str += f",{json_formatted_str}"
        else:
            journals_str += f"{json_formatted_str}"
    return journals_str


# Create a connection to Elasticsearch
# Create the parent index
def create_parent_index(parent_index):
    es = establish_connection_to_index()
    index_exists = es.indices.exists(index=parent_index)

    if index_exists:
        return

    mapping = {
        "mappings": {
            "properties": {
                "metadata": {
                    "properties": {"date": {"type": "date", "format": "yyyy-MM-dd"}}
                }
            }
        },
        "settings": {"index.mapping.total_fields.limit": 1000000},
    }

    es.indices.create(index=parent_index, body=mapping)


# Create a connection to Elasticsearch
# Update the parent index with new content
def add_document_to_index(parent_index, doc_index_id, content):
    es = establish_connection_to_index()
    doc_id_exists = es.exists(index=parent_index, id=doc_index_id)
    doi = content["metadata"]["doi"]
    table_id = content["metadata"]["table_id"]
    doi_results = search_index_by_doi(doi)
    doi_found = doi_results != "No results"
    same_table_exists = doi_found and same_table_id_found(doi_results, table_id)

    if doc_id_exists or same_table_exists:
        return -1

    es.index(index=parent_index, id=doc_index_id, body=content)
    return 0


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
    return collect_search_results(results)


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

    return collect_search_results(results)


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
    return collect_search_results(results)


# Force refresh index to make sure it is updated
def refresh_index(index_name):
    es = establish_connection_to_index()
    es.indices.refresh(index=index_name)


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
    return collect_search_results(results)


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
    journal_name = adjust_journal_name(journal)
    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {"match_phrase": {"metadata.journal": journal_name}},
    }

    results = es.search(body=query)
    return collect_search_results(results)


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
    return collect_search_results(results)


# Create a connection to Elasticsearch
# Search documents by paper doi
def search_index_by_doi(doi, maximum_results=2000):
    es = establish_connection_to_index()

    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {"match": {"metadata.doi": doi}},
    }

    results = es.search(body=query)
    return collect_search_results(results)


# Create a connection to Elasticsearch
# Search documents by author name and journal
def search_index_by_author_and_journal(author, journal, maximum_results=2000):
    es = establish_connection_to_index()
    journal_name = adjust_journal_name(journal)
    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {
            "bool": {
                "must": [
                    {"match": {"metadata.author(s)": author}},
                    {"match": {"metadata.journal": journal_name}},
                ]
            }
        },
    }

    results = es.search(body=query)
    return collect_search_results(results)


# Create a connection to Elasticsearch
# Search documents by author name and year
def search_index_by_author_and_year(author, year, maximum_results=2000):
    es = establish_connection_to_index()
    start_date = format_date(f"{str(year)}-01-01")
    end_date = format_date(f"{str(year)}-12-31")
    query = {
        "from": minimum_results,
        "size": maximum_results,
        "query": {
            "bool": {
                "must": [
                    {"match": {"metadata.author(s)": author}},
                    {
                        "range": {
                            "metadata.date": {
                                "gte": start_date,
                                "lte": end_date,
                            }
                        }
                    },
                ]
            }
        },
    }

    results = es.search(body=query)
    return collect_search_results(results)


# Format date in order to guarantee its type in elastic document
def format_date(date):
    d = dt.datetime.strptime(str(date).replace("/", "-"), "%Y-%m-%d")
    d = d.date()
    return d.isoformat()
