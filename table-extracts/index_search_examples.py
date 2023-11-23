from elastic_index import (
    search_index_by_author,
    search_index_by_year,
    search_index_by_year_range,
    search_index_by_journal,
    search_index_by_title,
    search_index_by_table_caption,
    search_index_by_word_in_table,
)


def main():
    parent_index = "astro"
    author = "Liodakis"
    journal = "Astronomy & Astrophysics"
    title = "Investigating the origin of stellar masses"
    content = "CMFs and predicted IMFs"
    year = 2022
    start_year = 2012
    end_year = 2019
    word = "a linear function with the mass of є_core ∝ M"
    # if you don't specify maximum_results in the functions below, the default value will be 2000
    maximum_results = 1500

    results = search_index_by_title(title, maximum_results)
    print(results)

    results = search_index_by_author(author)
    print(results)

    results = search_index_by_year(year)
    print(results)

    results = search_index_by_year_range(start_year, end_year, maximum_results)
    print(results)

    results = search_index_by_journal(journal)
    print(results)

    results = search_index_by_table_caption(content, maximum_results)
    print(results)

    results = search_index_by_word_in_table(parent_index, word)
    print(results)


main()
