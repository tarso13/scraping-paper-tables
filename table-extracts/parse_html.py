from bs4 import BeautifulSoup
import os
import json
from elastic_index import *
from aanda_parser import *
from iopscience_parser import *
from mnras_parser import *
from datetime import datetime, date

# List containing the html files with tables that have been extracted
files_extracted = []

# Map containing an (extra) url as key and a table suffix as value
url_suffixes = {}


# Get file content
def get_file_content(filepath):
    file = open(filepath, "r", encoding="utf-8")
    content = file.read()
    file.close()
    return content


# Include '^' in sup tags text indicating power exponentiation
def replace_sup_tags(soup_content):
    sup_tags = soup_content.find_all("sup")
    if sup_tags == None:
        return
    for sup_tag in sup_tags:
        sup_text = sup_tag.get_text()
        if not sup_tag.contents or not sup_tag.contents[0].string:
            continue
        sup_tag.contents[0].string.replace_with(f"^{sup_text}")

    return soup_content


# Include '_' in sub tags text indicating subscripts
def replace_sub_tags(soup_content):
    sub_tags = soup_content.find_all("sub")
    if sub_tags == None:
        return
    for sub_tag in sub_tags:
        sub_text = sub_tag.get_text()
        if sub_tag.contents[0].string == None:
            sub_tag.contents[0].string = ""
            sub_tag.contents[0].string.replace("", f"_{sub_text}")
        else:
            sub_tag.contents[0].string.replace_with(f"_{sub_text}")

    return soup_content


# Extract all tables from html file provided in html form and extra footnotes for journals
# Also replace sup and sub tags representing actual values
def extract_html_tables(soup_content):
    supplements = []
    updated_soup = replace_sup_tags(soup_content)
    re_updated_soup = replace_sub_tags(updated_soup)
    tables = re_updated_soup.find_all("table")
    for table in tables:
        parent_element = table.parent
        if "Only a portion of " in parent_element.get_text():
            supplements.append("true")
        else:
            supplements.append("false")
    return tables, supplements


# Search journal metadata (authors, title, date, journal) and return a map with the values (in json format)
def search_metadata(soup_content):
    metadata = {}
    metas = soup_content.find_all("meta")
    authors = []
    for meta in metas:
        content = meta.get("content")
        name = meta.get("name")
        match name:
            case "citation_author":
                authors.append(content)
            case "citation_journal_title":
                if not "journal" in metadata:
                    metadata["journal"] = content
            case "citation_title":
                if not "paper_title" in metadata:
                    metadata["paper_title"] = content
            case "citation_publication_date":
                date = format_date(content)
                if not "date" in metadata:
                    metadata["date"] = date
            case "citation_online_date":
                date = format_date(content)
                if not "date" in metadata:
                    metadata["date"] = date
            case "citation_doi":
                if not "doi" in metadata:
                    metadata["doi"] = content
    if not "author(s)" in metadata:
        metadata["author(s)"] = authors
    return metadata


# Extract aanda journal metadata
def extract_journal_metadata(soup_content):
    metadata = search_metadata(soup_content)
    return metadata


# Convert and add footnote to json object depending on journal
def footnote_to_json_object(journal, footnotes, entry, json_obj, key_prefix):
    if journal == "A&A":
        search_and_add_aanda_footnote_to_obj(footnotes, entry, json_obj)
    if journal == "IOPscience":
        search_and_add_iopscience_footnote_to_obj(
            footnotes, entry, json_obj, key_prefix
        )
    if journal == "mnras":
        search_and_add_mnras_footnote_to_obj(footnotes, entry, json_obj)
    return json_obj


# Convert list of data extracted from table to json array
def convert_to_json_array(list, json_data, key_prefix, footnotes, journal, header):
    if len(list) == 0:
        return
    json_objects = []
    counter = 1
    for entry in list:
        json_obj = {}
        index = f"col{str(counter)}"
        entry_content = ""
        if entry == None:
            entry_content = None
        else:
            entry_content = str(entry)
        json_obj[index] = {"content": entry_content}
        if header == True:
            json_obj[index]["header"] = "true"
        if footnotes:
            footnote_to_json_object(
                journal, footnotes, entry, json_obj[index], key_prefix
            )

        json_objects.append(json_obj)
        counter += 1
    json_data[key_prefix] = json_objects


# Add metadata and table info in json data for a table
def table_info_to_json_data(metadata, table_info, json_data):
    if "table_headers" in metadata:
        if len(list(metadata["table_headers"])) == 0:
            metadata.pop("table_headers")
    json_data["metadata"] = metadata
    json_data["table_info"] = table_info


# Add extra metadata in json data for a table
def include_extra_metadata_json_data(extra_metadata, metadata, json_data):
    for key in extra_metadata:
        metadata[key] = extra_metadata[key]
    json_data["metadata"] = metadata


# Extract table id from title using regex
def extract_table_id(title):
    # The regular expression pattern for '_T' followed by one or more digits (\d+)
    pattern = r"_T\d+"
    table_ids = re.findall(pattern, title)
    if not table_ids:
        return None
    table_id = table_ids[0].replace("_", "")
    return table_id


# Reorganise headers in a way that empty cells are identified and handled correctly
def reorganise_headers_as_rows(headers_as_rows, empty_row_cell):
    if len(headers_as_rows) < 1:
        return headers_as_rows
    for i in range(0, len(headers_as_rows)):
        index = i
        if index not in empty_row_cell:
            continue
        reorganised_next_row = [""] * len(headers_as_rows[index])
        if len(empty_row_cell[index]):
            for i in range(0, len(headers_as_rows[index])):
                if i in empty_row_cell[index]:
                    continue
                else:
                    current_next_row = headers_as_rows[index + 1]
                    if len(current_next_row):
                        reorganised_next_row[i] = current_next_row[0]
                        current_next_row.pop(0)
                        headers_as_rows[index + 1] = current_next_row
            headers_as_rows[index + 1] = reorganised_next_row
    return headers_as_rows


# Extract all table data by reading the table headers first,
# and then all table rows as well as their data
# All row data extracted are printed as lists
# and then converted into json files
def extract_table_data(
    table, title, footnotes, metadata, extra_metadata, table_info, supplementary
):
    json_data = {}
    current_table_info = {}

    if "A&A" in title:
        current_table_info = table_info

    if "IOPscience" in title:
        current_table_info = table_info
        if "notes" in current_table_info and current_table_info["notes"] == "":
            current_table_info.pop("notes")

    headers_as_rows = []
    key_prefix = ""
    table_rows = table.find_all("tr")
    empty_row_cell = {}
    for tr in table_rows:
        headers = []
        index = table_rows.index(tr)
        empty_row_cell[index] = []
        ths = tr.find_all("th")
        for th in ths:
            col_index = ths.index(th)
            if "</th>" not in str(th):
                continue
            if 'rowspan="2"' in str(th):
                empty_row_cell[index].append(col_index)
            text = th.get_text().replace("\xa0", EMPTY).replace("\n", "").strip()
            header = re.sub(r"\s+", " ", text)
            header = re.sub(r"\s+\.", ".", header)
            if header == "":
                span = th.find("span")
                if span:
                    img = span.find("img")
                    if img:
                        data = "unparsable (img)"
            if header:
                if header[-1] == ".":
                    header = header[:-1]

            if header == " " or header == "":
                header = None
            headers.append(header)
        if len(headers) and headers not in headers_as_rows:
            headers_as_rows.append(headers)
    headers_as_rows = reorganise_headers_as_rows(headers_as_rows, empty_row_cell)

    if "MNRAS" in title:
        table_id = identify_mnras_table_id(table)
        if table_id == -1:
            return
        table_suffix = f"T{table_id}"
        if f"_{table_suffix}" not in title:
            title += f"_{table_suffix}"
        metadata["table_id"] = table_suffix
        current_table_info = search_mnras_table_info_and_footnotes(table)
    else:
        table_id = extract_table_id(title)
        metadata["table_id"] = table_id

    table_info_to_json_data(metadata, current_table_info, json_data)

    if supplementary == "true":
        json_data["supplementary"] = "true"

    mnras_headers = []
    if len(headers_as_rows):
        prev_index = 0
        prev_headers = []
        extra_metadata[f"table_headers"] = {}
        for headers_as_row in headers_as_rows:
            index = headers_as_rows.index(headers_as_row) + 1
            if index == prev_index or prev_headers == headers_as_row:
                continue
            if prev_index != 0 and index != (prev_index + 1):
                index = prev_index + 1
            key_prefix = f"row{str(index)}"
            extra_metadata[f"table_headers"][str(index)] = headers_as_row
            mnras_headers.append(headers_as_row)
            prev_index = index
            prev_headers = headers_as_row

    extra_metadata["table_rows"] = 0
    extra_metadata["table_cols"] = 0
    if len(headers_as_rows):
        extra_metadata["table_cols"] = len(list(headers_as_rows[0]))

    journal = ""
    valid_footnotes = {}

    if "IOPscience" in title:
        journal = "IOPscience"
        valid_footnotes = footnotes

    if "A&A" in title:
        journal = "A&A"
        if len(headers_as_rows):
            valid_footnotes = validate_aanda_footnotes(
                footnotes, valid_footnotes, headers_as_rows[0]
            )

    if "MNRAS" in title:
        journal = "mnras"
        valid_footnotes = mnras_footnotes

    if journal == "mnras":
        headers_as_rows = mnras_headers

    if headers_as_rows:
        convert_to_json_array(
            headers_as_rows[0], json_data, f"row1", valid_footnotes, journal, True
        )

    if len(headers_as_rows):
        for headers_as_row in headers_as_rows:
            index = headers_as_rows.index(headers_as_row) + 1
            key_prefix = f"row{str(index)}"
            if "A&A" in title:
                valid_footnotes = validate_aanda_footnotes(
                    footnotes, valid_footnotes, headers
                )
            if "IOPscience" in title:
                valid_footnotes = footnotes

            valid_footnotes = mnras_footnotes
            convert_to_json_array(
                headers_as_row, json_data, key_prefix, valid_footnotes, journal, True
            )
    cell_to_add = {}
    for row in table_rows:
        row_index = table_rows.index(row) + 1
        index = row_index
        key_prefix = f"row{str(index)}"
        data_found = []
        tds = row.find_all("td")
        for td in tds:
            data = str(
                td.get_text()
                .replace("\xa0", EMPTY)
                .replace("\n", EMPTY)
                .replace("  ", "")
            )
            col_index = tds.index(td)
            if 'rowspan="2"' in str(td):
                cell_to_add[index + 1] = [str(col_index), data]

            if index in cell_to_add and str(col_index) in cell_to_add[index]:
                data = cell_to_add[index][1]

            if data == "":
                span = td.find("span")
                if span:
                    img = span.find("img")
                    if img:
                        data = "unparsable (img)"
            if data:
                if data[-1] == ".":
                    data = data[:-1]

                if data == " ":
                    data = None

            data_found.append(data)

        if row_index == 1:
            extra_metadata["table_rows"] = len(table_rows)
            if not len(headers_as_rows):
                extra_metadata["table_cols"] = len(data_found)

            include_extra_metadata_json_data(extra_metadata, metadata, json_data)

        if "A&A" in title:
            valid_footnotes = validate_aanda_footnotes(
                footnotes, valid_footnotes, data_found
            )
        if "IOPscience" in title:
            valid_footnotes = footnotes
        convert_to_json_array(
            data_found, json_data, key_prefix, valid_footnotes, journal, False
        )

    keys = list(json_data["metadata"].keys())
    keys.sort()
    json_data["metadata"] = {i: json_data["metadata"][i] for i in keys}

    write_to_json_file("json_results", f"{title}", json_data)
    return json_data


# Write json data to json file
# Title is the title of the json file
# Directory name is the directory the json file will be stored
def write_to_json_file(directory_name, title, json_data):
    if not os.path.isdir(directory_name):
        os.mkdir(directory_name)
    path_to_json = os.path.join(directory_name, f"{title}.json")
    file = open(path_to_json, "w", encoding="utf-8")
    file.write(json.dumps(json_data, indent=1))


# Append document in order to update the parent elastic index
def append_to_elastic_index(parent_index, doc_index_id, content):
    return add_document_to_index(parent_index, doc_index_id, content)


# Extract all table data found in html files in given directory and print them
def extract_downloaded_tables(directory_name):
    if os.path.exists(directory_name) == False:
        return

    parent_index_name = "astro"
    mrt_parent_index_name = "mrt_astro"

    for entry in os.listdir(directory_name):
        path_to_entry = os.path.join(directory_name, entry)
        # os.listdir returns both directories and files included in diretory given
        if os.path.isfile(path_to_entry) == False:
            continue

        if entry in files_extracted:
            continue

        files_extracted.append(entry)

        print("\nResults for " + entry)
        entry_content = get_file_content(path_to_entry)

        soup_content = BeautifulSoup(entry_content, "html.parser")

        if "A&A" in entry and "A&A_T" not in entry:
            title_to_metadata[entry] = extract_journal_metadata(soup_content)
            continue

        tables, supplements = extract_html_tables(soup_content)
        footnotes = None
        metadata = {}
        extra_metadata = {}
        table_info = {}

        if "Captcha" in entry:
            continue

        if "A&A" in entry:
            metadata = search_aanda_journal_metadata(entry)
            d = dt.datetime.strptime(metadata["date"], "%Y-%m-%d")
            year = d.year
            footnotes = search_aanda_footnotes(soup_content, year)
            table_info = search_aanda_table_info(soup_content)

        mrt_indexes = {}

        if "IOPscience" in entry:
            metadata = extract_journal_metadata(soup_content)

            mrt_titles, json_results = extract_iopscience_mrt_tables(
                soup_content, "iopscience_mrts"
            )

            for result in json_results:
                index = json_results.index(result)
                mrt_title = mrt_titles[index]
                result["metadata"]["doi"] = metadata["doi"]
                write_to_json_file("json_mrts", mrt_title, result)
                mrt_indexes[mrt_title] = result

        refresh_index(parent_index_name)
        doc_index_id = get_next_document_id(parent_index_name)
        for table in tables:
            title = entry.replace(".html", "")

            index = tables.index(table)
            if "IOPscience" in title:
                title += f"_T{str(index + 1)}"

            metadata["retrieval_date"] = str(date.today())
            if "MNRAS" in title:
                (
                    publication_date,
                    journal,
                    authors,
                    paper_title,
                    doi,
                ) = extract_mnras_extra_metadata(soup_content)
                metadata["journal"] = journal
                formatted_date = format_date(publication_date)
                metadata["date"] = formatted_date
                metadata["authors"] = authors
                metadata["doi"] = doi
                metadata["paper_title"] = paper_title
                if (
                    not publication_date
                    or not journal
                    or not authors
                    or not paper_title
                    or not doi
                ):
                    metadata = extract_journal_metadata(soup_content)

                if "IOPscience" in title:
                    footnotes = search_iopscience_footnotes(table, table_info)
                    table_info["caption"] = search_iopscience_table_caption(table)
                    table_info["notes"] = search_iopscience_table_notes(table)

            json_data = extract_table_data(
                table,
                title,
                footnotes,
                metadata,
                extra_metadata,
                table_info,
                supplements[index],
            )
            if not json_data:
                continue

            ret_code = append_to_elastic_index(
                parent_index_name, doc_index_id, json_data
            )

            if ret_code == -1:
                assert False
            doc_index_id += 1

        if mrt_indexes:
            refresh_index(mrt_parent_index_name)
            mrt_doc_index_id = get_next_document_id(mrt_parent_index_name)
            for mrt_index in mrt_indexes:
                ret_code = append_to_elastic_index(
                    mrt_parent_index_name, mrt_doc_index_id, mrt_indexes[mrt_index]
                )
                if ret_code == -1:
                    assert False
                mrt_doc_index_id += 1
