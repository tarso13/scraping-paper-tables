from download_html import download_all_html_files
from parse_html import (
    extract_downloaded_tables,
    create_parent_index,
)


def read_urls_from_file(filename):
    file = open(filename, "r", encoding="utf-16")
    urls = file.readlines()
    urls_updated = []
    for url in urls:
        url = str(url).rstrip()
        urls_updated.append(url)
    return urls_updated


# Main function to download initial urls and extract data
def main():
    create_parent_index("astro")
    create_parent_index("mrt_astro")
    aanda_2022 = read_urls_from_file("aanda_2022.txt")
    download_all_html_files("pubs", aanda_2022, True)
    mnras_2022 = read_urls_from_file("mnras_2022.txt")
    download_all_html_files("pubs", mnras_2022, False)
    extract_downloaded_tables("pubs_aanda")
    extract_downloaded_tables("pubs_aanda/pubs_aanda_tables")
    extract_downloaded_tables("pubs_mnras")
    extract_downloaded_tables("pubs_iopscience")


main()
