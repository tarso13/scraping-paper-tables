from download_html import *
from parse_html import extract_downloaded_tables


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
    aanda_2022 = read_urls_from_file("aanda_2022.txt")
    download_all_html_files("pubs", aanda_2022, True)
    mnras_2022 = read_urls_from_file("mnras_2022.txt")
    download_all_html_files("pubs", mnras_2022, False)
    _ = extract_downloaded_tables("pubs_aanda", 0)
    doc_index_id = extract_downloaded_tables("pubs_aanda/pubs_aanda_tables", 1)
    _ = extract_downloaded_tables("pubs_mnras", doc_index_id + 1)


main()
