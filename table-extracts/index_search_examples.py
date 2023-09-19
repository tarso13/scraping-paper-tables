from elastic_index import search_index_by_author, search_index_by_year, search_index_by_year_range, search_index_by_journal, search_index_by_title, search_index_by_table_caption

def main():
    index_name = 'astro'
    author = 'Liodakis'
    journal = 'The Astronomical Journal'
    title = 'Toy model for the acceleration of blazar jets'
    content = 'Radial velocity'
    year = 2017
    start_year = 2012
    end_year = 2019
    
    results = search_index_by_title(index_name, title)
    print(results)
    
    results = search_index_by_author(index_name, author)
    print(results)
    
    results = search_index_by_year(index_name, year)
    print(results)

    results = search_index_by_year_range(index_name, start_year, end_year)
    print(results)
    
    results = search_index_by_journal(index_name, journal)
    print(results)
    
    results = search_index_by_table_caption(index_name, content)
    print(results)

main()