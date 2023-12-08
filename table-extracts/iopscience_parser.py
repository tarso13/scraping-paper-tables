import re
import os
import astropy.io.ascii as ascii
import requests

# Value used to replace undesired word occurences in datasets
EMPTY = ""

mrt_keys = 0


# Find iopscience footnotes using regex
# They are declared using '^', an empty space ' ' and a letter
def find_iopscience_footnotes(string):
    pattern = r"\^ [a-zA-Z]"
    matches = re.findall(pattern, string)
    return matches


# Search for footnote in IOPscience list of data and if found, add it to the json object the entry belongs to
def search_and_add_iopscience_footnote_to_obj(footnotes, data, json_obj, key_prefix):
    for footnote in footnotes:
        index = footnotes.index(footnote)
        for key in footnote.keys():
            actual_key = key.replace(" ", "")
            if actual_key in data:
                json_obj["content"] = json_obj["content"].replace(f"{actual_key}", "")
                note = footnotes[index]
                json_obj["note"] = note[key].strip()
                if "table_headers" in key_prefix:
                    footnotes.remove(footnote)


# If notes include footnote value, remove notes
# because the information is present in table cells
def remove_footnote_from_notes(res, table_info):
    for note in table_info["notes"]:
        if res in note:
            index = table_info["notes"].index(note)
            table_info["notes"][index] = ""


# Identify footnotes in iopscience journal and if they belong to a header,
# then remove them because they are only encountered once
# However, if they belong to rows containing table data they are likely encountered multiple
# times. Hence, we should keep this information
def identify_iopscience_footnotes(small_tag, footnotes, table_info):
    footnote_value = (
        small_tag.get_text()
        .replace("\n", "")
        .replace("  ", "")
        .replace("Notes.", "")
        .replace("Note.", "")
        .strip()
    )
    result = find_iopscience_footnotes(footnote_value)
    footnote_values = footnote_value.split(".^")
    for splitted_value in footnote_values:
        index = footnote_values.index(splitted_value)
        if splitted_value[0] != "^":
            footnote_values[index] = f"^{splitted_value}"
        if splitted_value[-1] != ".":
            footnote_values[index] = f"{splitted_value}."

    for res in result:
        for splitted_value in footnote_values:
            if res in splitted_value:
                footnotes.append({res: splitted_value.replace(res, "").strip()})
        # remove_footnote_from_notes(res, table_info)
    return footnotes


# Search for footnotes in iopscience journal
def search_iopscience_footnotes(soup_content, table_info):
    small_tags = soup_content.parent.find_all("small")
    if small_tags == None:
        return

    footnotes = []
    for small_tag in small_tags:
        sup_tag = small_tag.find("sup")
        if sup_tag == None:
            continue
        sup_text = sup_tag.get_text().replace(" ", "").replace("\n", "")
        if sup_text == None:
            continue
        sup_value = sup_text.replace("^", "")
        if sup_value.isalpha():
            identify_iopscience_footnotes(small_tag, footnotes, table_info)

    return footnotes


# Search for table notes in iopscience journal
def search_iopscience_table_notes(soup_content):
    notes = ""
    p_tags = soup_content.parent.find_all("p")
    for p_tag in p_tags:
        small_tag = p_tag.find("small")
        if small_tag == None:
            continue
        strong_tag = small_tag.find("strong")
        if strong_tag == None:
            continue
        notes = small_tag.get_text().replace("\n", "").replace("  ", "")
        return notes
    return notes


# Search for table captions in iopscience journal
def search_iopscience_table_caption(soup_content):
    p_tags = soup_content.parent.find_all("p")
    caption = ""
    for p_tag in p_tags:
        b_tag = p_tag.find("b")
        if b_tag == None:
            continue
        if "Table" not in b_tag.get_text():
            continue
        caption = p_tag.get_text().replace(b_tag.get_text(), "").replace("\xa0", EMPTY)
        return caption
    return caption


# Search for table info in iopscience journal, including notes and caption
def search_iopscience_table_info(soup_content):
    table_info = {}

    table_info["caption"] = search_iopscience_table_caption(soup_content)

    return table_info


# Write mrt file containing full versions for tables of iopscience journals
def write_mrt_file(directory_name, title, content):
    if not os.path.isdir(directory_name):
        os.mkdir(directory_name)
    path_to_mrt = os.path.join(directory_name, f"{title}.txt")
    if os.path.exists(path_to_mrt):
        return
    file = open(path_to_mrt, "wb")
    file.write(content)


# Convert mrt table units and header explanations to json format
def mrt_headers_to_json(units, explanations, json_data):
    if "metadata" not in json_data:
        json_data["metadata"] = {}
    json_data["metadata"]["units"] = units
    json_data["metadata"]["header explanations"] = explanations
    return json_data


# Convert mrt table data to json format
def mrt_table_data_to_json(mrt_table, json_data):
    keys = []
    key_indexes = {}
    key_count = 0
    for key in mrt_table:
        key_count += 1
        keys.append({"content": str(key), "header": "true"})
        json_data["metadata"]["header explanations"][key_count - 1] = json_data[
            "metadata"
        ]["header explanations"][key_count - 1].strip()
        metadata_header = json_data["metadata"]["header explanations"][key_count - 1]
        if key in metadata_header:
            header_expl = f'{key} - {metadata_header.replace(key, "").strip()}'
            json_data["metadata"]["header explanations"][key_count - 1] = header_expl
        key_indexes[key] = str(key_count)

    for key in keys:
        key_index = keys.index(key)
        keys[key_index] = {f"col{key_index + 1}": keys[key_index]}
    json_data["row1"] = keys

    for key in mrt_table:
        counter = 1
        values = mrt_table[key]
        col_index = key_indexes[key]
        for value in values:
            if f"row{str(counter + 1)}" not in json_data:
                json_data[f"row{str(counter + 1)}"] = []
            json_data[f"row{str(counter + 1)}"].append(
                {f"col{str(col_index)}": {"content": str(values[value])}}
            )
            counter += 1

    return json_data


# The function extract_mrt_table_title, extract_mrt_authors, extract_mrt_table_caption
# are helper functions based on observation for the mrt files used in iopscience journals (html form)
# Thus, they should be used the order provided due to changes made to 'table_lines' while parsing the journal metadata.
def extract_mrt_table_title(table_lines):
    title = ""
    for line in table_lines:
        if "Authors:" in line:
            break
        title += line
        index = table_lines.index(line)
        table_lines[index] = ""
    title = title.replace("Title:", "").strip()
    return title


def extract_mrt_authors(table_lines):
    authors = ""
    for line in table_lines:
        if "Table:" in line:
            break
        authors += line
        index = table_lines.index(line)
        table_lines[index] = ""
    authors = authors.replace("Authors:", "")

    return authors


def extract_mrt_table_caption(table_lines):
    caption = ""
    split_point = "================================================================================"
    for line in table_lines:
        if split_point in line:
            break
        caption += line
    caption = caption.replace("Table:", "").strip()
    return caption


# Extract mrt metadata (title, authors and caption) for mrt table
def extract_mrt_metadata(table_lines):
    title = extract_mrt_table_title(table_lines)
    authors = extract_mrt_authors(table_lines)
    caption = extract_mrt_table_caption(table_lines)
    return title, authors, caption


# Convert mrt metadata to json
def mrt_metadata_to_json(title, authors, caption, json_data):
    json_data["metadata"] = {}
    json_data["metadata"]["paper_title"] = title
    json_data["metadata"]["authors"] = authors
    json_data["metadata"]["caption"] = caption
    return json_data


def extract_mrt_units_and_explanations(table_lines):
    units = []
    explanations = []
    header_line = 0
    first_data_line = 0
    split_point = "--------------------------------------------------------------------------------"
    for line in table_lines:
        line_index = table_lines.index(line)

        if "Units" in line:
            header_line = line_index
            first_data_line = header_line + 2

        if header_line == 0:
            continue

        if split_point in line and len(units) != 0:
            break

        if line_index > header_line and line_index >= first_data_line:
            line_list = list(line.replace("  ", " ").split(" "))
            units.append(line_list[5])
            explanation = ""
            for i in range(6, len(line_list)):
                word = line_list[i].replace("\n", "")
                if line_list[i] != " ":
                    explanation += f"{word} "
            explanations.append(explanation)

    return units, explanations


# Extract mrt files containing full versions for tables of iopscience journals from their html content
# and write the data in bytes in local mrt files
def extract_iopscience_mrt_tables(soup_content, directory_name):
    web_refs = soup_content.find_all("a", {"class": "webref"})
    json_results = []
    mrt_titles = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    for web_ref in web_refs:
        if "machine-readable" in web_ref.get_text():
            href = web_ref["href"]
            # mrt_html = requests.get(href, headers)
            mrt_title = extract_mrt_title(href)
            mrt_titles.append(mrt_title)
            # content = mrt_html.content
            # write_mrt_file(directory_name, mrt_title, content)
            path_to_mrt = os.path.join(directory_name, f"{mrt_title}.txt")

            mrt_file = open(path_to_mrt, "r")
            lines = mrt_file.readlines()
            # title, authors, caption = extract_mrt_metadata(lines)
            units, explanations = extract_mrt_units_and_explanations(lines)
            data = ascii.read(path_to_mrt, format="mrt")
            df = data.to_pandas()
            table = df.to_dict()
            json_data = {}
            # json_data = mrt_metadata_to_json(title, authors, caption, json_data)
            json_data = mrt_headers_to_json(units, explanations, json_data)
            json_data = mrt_table_data_to_json(table, json_data)
            json_results.append(json_data)
    return mrt_titles, json_results


# Extract title from href pointing to the mrt file
def extract_mrt_title(href):
    revision_index = href.find("revision1/")
    txt_index = href.find(".txt")
    title = href[revision_index + len("revision1/") : txt_index]
    return title
