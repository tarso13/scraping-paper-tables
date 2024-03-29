from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, date

from parse_html import (
    extract_table_data,
    extract_journal_metadata,
    search_aanda_footnotes,
    search_aanda_journal_metadata,
    search_aanda_table_info,
    extract_html_tables,
    title_to_metadata,
    append_to_elastic_index,
)
from tldextract import extract
from urllib.parse import urlparse
import os
import requests
import re

# Headers to be used when retrieving urls
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# List of invalid words which may be encountered in paper titles
invalid_characters_as_words = [
    "#",
    "<",
    "$",
    "+",
    "%",
    ">",
    "!",
    ".",
    "`",
    "*",
    "'",
    "|",
    "{",
    "?",
    "=",
    "}",
    "/",
    ":",
    '"',
    "\\",
    "@",
    ",",
]


# Create a directory with the name given (if it does not exist)
def create_directory(directory_name):
    if os.path.isdir(directory_name):
        return
    os.mkdir(directory_name)


# Identify the domain name and replace dots with underscores to save file locally
# Example: "http://abc.hostname.com/somethings/anything/"
def domain_from_url(url):
    tsd, td, tsu = extract(url)  # abc, hostname, com
    url_domain = f"{tsd}.{td}.{tsu}"
    return url_domain


# Find html title given the content of an html file
def fetch_title(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.title.string


# Download url provided and save it locally (html file)
# The directory to save the file is provided
# The name of the file is the new title generated from the title provided
def download_html_locally(url, directory_name, suffix, download_extra_files):
    try:
        create_directory(directory_name)
        downloaded_files = os.listdir(directory_name)

        print("Downloading " + url)
        
        response = requests.get(url, headers=headers)
        content = response.text
        new_title = None
        doi = get_doi(content)

        if "aanda" in directory_name:
            new_title = f"{doi}_A&A"

        if "mnras" in directory_name:
            new_title = f"{doi}_MNRAS"

        if "iopscience" in directory_name:
            new_title = f"{doi}_IOPscience"

        local_file = f"{new_title}{suffix}.html"

        if local_file in downloaded_files:
            print(f"Cancel download of {url} [Already exists]")
            return

        path_to_file = os.path.join(directory_name, local_file)

        with open(path_to_file, "w", encoding="utf-8") as file:
            file.write(content)

        if "A&A" in local_file and "A&A_T" not in local_file:
            path_to_extra_file = (
                f"{os.path.join(directory_name, directory_name)}_tables"
            )
            aanda_download_extra_files(
                content, path_to_extra_file, downloaded_files, download_extra_files
            )
    except requests.RequestException as e:
        print(str(e), " while retrieving ", url)


# Download html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_all_html_files(directory_name, urls, download_extra_files):
    for url in urls:
        new_directory_name = directory_name
        if "aanda" in domain_from_url(url):
            new_directory_name = f"{directory_name}_aanda"
        if "iopscience" in domain_from_url(url):
            new_directory_name = f"{directory_name}_iopscience"
        if "mnras" in url:
            new_directory_name = f"{directory_name}_mnras"
        download_html_locally(url, new_directory_name, "", download_extra_files)


# Build table suffix for local html file that contains extra table found in original html
def table_suffix(path_to_table):
    suffix_index = path_to_table.find("/T")
    html_index = path_to_table.find(".html")
    suffix = path_to_table[suffix_index:html_index]
    suffix = suffix.replace("/", "_")
    return suffix


# Identify the domain name given an html content using the base href tag
def domain(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    base = soup.find("base")
    base_href = base.get("href")
    domain = urlparse(base_href).netloc
    return domain


def get_doi(html_content):
    doi = None
    soup = BeautifulSoup(html_content, "html.parser")
    meta_doi = soup.find("meta", {"name": "citation_doi"})
    metadata = {}
    authors = []
    text = ""
    if meta_doi:
        doi = meta_doi.get("content")
        doi = doi.replace(".", "_").replace("/", "__")
        return doi

    script_tags = soup.find_all("script")
    for script_tag in script_tags:
        text = script_tag.get_text()
        if not text:
            continue
        if "var dataLayer" in text:
            break

    json_match = re.search(r"\[{.*}\];", text)
    if json_match:
        json_data = json_match.group()

        json_data = (
            json_data.replace("[", "")
            .replace(
                "]",
                "",
            )
            .replace(";", "")
        )
        json_data = json.loads(json_data)
        doi = json_data["doi"]
    if doi:
        return doi.replace(".", "_").replace("/", "__")
    metrics_element = soup.find("div", {"id": "metrics-tabs"})
    if metrics_element:
        doi = metrics_element.get("data-doi")
        return doi.replace(".", "_").replace("/", "__")

    altmetric_element = soup.find("div", {"class": "altmetric-embed"})
    if altmetric_element:
        doi = altmetric_element.get("data-doi")
        return doi.replace(".", "_").replace("/", "__")

    return None


# Find extra table files from initial aanda papers and download them
def aanda_download_extra_files(
    content, directory_name, downloaded_files, download_extra_files
):
    soup = BeautifulSoup(content, "lxml")
    table_classes = soup.findAll("div", {"class": "ligne"})
    url_suffixes = {}
    domain_found = domain(content)
    doi = get_doi(content)
    title_to_metadata[doi] = extract_journal_metadata(soup)
    for table_class in table_classes:
        path_to_table = table_class.find("a")["href"]
        full_path = f"https://{domain_found}{path_to_table}"
        suffix = table_suffix(path_to_table)
        if not download_extra_files:
            response = requests.get(full_path, headers=headers)
            content = response.text
            extract_undownloaded_tables(content, f"{doi}{suffix}", doi)
            continue
        html_local_path = f"{doi}{suffix}.html"
        url_suffixes[full_path] = suffix

        if html_local_path in downloaded_files:
            url_suffixes.pop(full_path)

    download_extra_html_files(directory_name, url_suffixes, download_extra_files)


# Download extra html files from urls and save them locally concurrently
# Specify aanda case and save those files in different directory
def download_extra_html_files(directory_name, url_suffixes, download_extra_files):
    for url in url_suffixes:
        download_html_locally(
            url, directory_name, str(url_suffixes[url]), download_extra_files
        )


# Extract all table data found in html content without downloading the extra files and print them
def extract_undownloaded_tables(content, title, entry):
    soup_content = BeautifulSoup(content, "html.parser")

    tables, _ = extract_html_tables(soup_content)

    parent_index_name = "astro"
    footnotes = None
    metadata = {}
    extra_metadata = {}
    table_info = {}

    if "A&A" in title:
        metadata = search_aanda_journal_metadata(entry)
        d = datetime.strptime(metadata["date"], "%Y-%m-%d")
        year = d.year
        footnotes = search_aanda_footnotes(soup_content, year)
        table_info = search_aanda_table_info(soup_content)

    metadata["retrieval_date"] = str(date.today())
    metadata["paper_access_property"] = "open"

    for table in tables:
        index = tables.index(table)

        json_data = extract_table_data(
            table,
            title,
            footnotes,
            metadata,
            extra_metadata,
            table_info,
            index,
            "false",
        )

        if not json_data:
            continue

        ret_code = append_to_elastic_index(parent_index_name, doc_index_id, json_data)

        if ret_code == -1:
            continue

        doc_index_id += 1

        append_to_elastic_index(parent_index_name, doc_index_id, json_data)
