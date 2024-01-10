from elastic_index import (
    search_index_by_author,
    search_index_by_year,
    search_index_by_year_range,
    search_index_by_journal,
    search_index_by_title,
    search_index_by_table_caption,
    search_index_by_word_in_table,
    search_index_by_doi,
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
    # if you don't specify maximum_results in the functions below, the default value will be 10000
    maximum_results = 1500

    # results = search_index_by_title(title, parent_index, maximum_results)
    # print(results)

    # results = search_index_by_doi("10.1093/mnras/stab3111", parent_index)
    # print(results)

    # results = search_index_by_year(year, parent_index)
    # print(results)

    # results = search_index_by_year_range(
    #     start_year, end_year, parent_index, maximum_results
    # )
    # print(results)

    results = search_index_by_journal(journal, parent_index)
    print(results)

    # results = search_index_by_table_caption(content, parent_index, maximum_results)
    # print(results)

    # results = search_index_by_word_in_table(parent_index, word)
    # print(results)


main()
