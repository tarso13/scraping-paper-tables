from upload_elastic_index import search_index_by_author, search_index_by_date, search_index_by_journal, search_index_by_title, search_index_by_table_caption

def main():
    index_name = 'astro'
    start_date = '2016-01-01'
    end_date = '2016-02-01'
    author = 'Liodakis'
    journal = 'mnras'
    title = 'Toy model for the acceleration of blazar jets'
    content = 'Radial velocity'
    
    results = search_index_by_title(index_name, title)
    print(results)
    
    results = search_index_by_author(index_name, author)
    print(results)
    
    results = search_index_by_date(index_name, start_date, end_date)
    print(results)
    
    results = search_index_by_journal(index_name, journal)
    print(results)
    
    results = search_index_by_table_caption(index_name, content)
    print(results)

main()