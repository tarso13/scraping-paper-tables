from elastic_index import (
    search_index_by_author,
    search_index_by_year,
    search_index_by_year_range,
    search_index_by_journal,
    search_index_by_title,
    search_index_by_table_caption,
    search_index_by_doi,
)


def main():
    parent_index = "astro"
    author = "Jackson"
    journal = "Astronomy & Astrophysics"
    title = "Investigating the origin of stellar masses"
    content = "amplitude of periodic"
    year = 2022
    start_year = 2022
    end_year = 2023
    # if you don't specify maximum_results in the functions below, the default value will be 10000
    maximum_results = 1500

    results = search_index_by_title(title, parent_index, maximum_results)
    print(results)

    results = search_index_by_doi("10.1093/mnras/stab3111", parent_index)
    print(results)

    results = search_index_by_year(year, parent_index)
    print(results)

    results = search_index_by_year_range(
        start_year, end_year, parent_index, maximum_results
    )
    print(results)

    results = search_index_by_journal(journal, parent_index)
    print(results)

    results = search_index_by_table_caption(content, parent_index, maximum_results)
    print(results)

    results = search_index_by_author(author, parent_index)
    print(results)


main()
