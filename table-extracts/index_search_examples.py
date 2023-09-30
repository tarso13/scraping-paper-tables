from elastic_index import search_index_by_author, search_index_by_year, search_index_by_year_range, search_index_by_journal, search_index_by_title, search_index_by_table_caption, search_index_by_word_in_table

def main():
    index_name = 'astro'
    author = 'Liodakis'
    journal = 'The Astronomical Journal'
    title = 'Toy model for the acceleration of blazar jets'
    content = 'Radial velocity'
    year = 2022
    start_year = 2012
    end_year = 2019
    word = 'Ellipses'
    # if you don't specify maximum_results in the functions below, the default value will be 2000
    maximum_results = 1500
    
    results = search_index_by_title(index_name, title, maximum_results)
    print(results)
    
    results = search_index_by_author(index_name, author)
    print(results)

    results = search_index_by_year(index_name, year)
    print(results)

    results = search_index_by_year_range(index_name, start_year, end_year, maximum_results)
    print(results)
    
    results = search_index_by_journal(index_name, journal)
    print(results)
    
    results = search_index_by_table_caption(index_name, content, maximum_results)
    print(results)
    
    results = search_index_by_word_in_table(index_name, word)
    print(results)

main()