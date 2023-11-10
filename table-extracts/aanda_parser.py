# Value used to replace undesired word occurences in datasets
EMPTY = ""

# Map containing the initial aanda title as key with its metadata as value
title_to_metadata = {}


# Search for footnotes in aanda articles
def search_aanda_footnotes(soup_content, year):
    notes_section = None
    footnotes_kvs = {}

    if year == 2022:
        notes_section = soup_content.find("div", {"class": "history"})
        if notes_section:
            footnote_divs = notes_section.find_all("div")
            for footnote_div in footnote_divs:
                a_tag = footnote_div.find("a")
                if a_tag and "TFN" in a_tag["name"]:
                    footnote_split = footnote_div.find("p").get_text()  # .split(')')
                    if not footnote_div.find("sup"):
                        break
                    else:
                        footnote_sup = footnote_div.find("sup").get_text()
                    footnotes_kvs[footnote_sup] = footnote_split
        if footnotes_kvs:
            return footnotes_kvs
    else:
        notes_section = soup_content.find("div", {"class_": "history"})

    if not notes_section or not notes_section.find("p"):
        return None

    notes = (
        notes_section.find("p")
        .get_text()
        .replace("Notes.", "")
        .replace("Note.", "")
        .strip()
    )

    split_notes = notes.split("^")
    split_notes.pop(0)
    for split_note in split_notes:
        split_note = f"^{split_note}"

    labels = notes_section.find_all("sup")

    if len(labels) > len(split_notes):
        return None

    for label in labels:
        index = labels.index(label)
        label_name = label.get_text(strip=True)
        label_text = ""
        if year == 2022:
            label_text = split_notes[index].replace(label_name.replace("^", ""), "")
        else:
            label_text = label.find_next("p").get_text(strip=True)
        footnotes_kvs[label_name] = label_text
    return footnotes_kvs


# Search and extract table description and notes
def search_aanda_table_info(soup_content):
    table_info = {}

    notes_section = soup_content.find("div", {"class": "history"})
    if not notes_section:
        notes_section = soup_content.find("div", {"class_": "history"})

    description_section = soup_content.find("div", id="annex")

    if not notes_section and description_section.find("p"):
        table_info["caption"] = description_section.find("p").get_text(strip=True)
        return table_info

    if not description_section:
        return None

    table_info["caption"] = description_section.find("p").get_text(strip=True)

    notes_element = notes_section.find("p")
    if notes_element:
        table_info["notes"] = notes_element.get_text(strip=True).replace("Notes.", "")

    p_tags = notes_section.find_all("p")
    for p_tag in p_tags:
        b_tag = p_tag.find("b")
        if not b_tag:
            continue
        if "References" in b_tag.get_text():
            table_info["references"] = p_tag.get_text().replace(b_tag.get_text(), "")
            break

    if "notes" in table_info and table_info["notes"] == "":
        notes_text = ""
        notes = notes_section.find_all("div")
        for note in notes:
            notes_text += note.get_text()
        table_info["notes"] = notes_text

    return table_info


# Validate footnotes found through initial parsing and returns only the correct ones
def validate_aanda_footnotes(footnotes, valid_footnotes, data_found):
    if not footnotes:
        return None
    for footnote in footnotes:
        value = footnote.replace("(", "").replace(")", "").replace("^", "")
        int_footnote = value.isnumeric()
        if int_footnote and int(value) < 0:
            continue
        for data in data_found:
            detected_footnote = ""
            if footnote in data:
                detected_footnote = footnote
            if f"^{value}" in data:
                detected_footnote = f"^{value}"
            if f"^({value})" in data:
                detected_footnote = f"^({value})"
            if detected_footnote != "":
                valid_footnotes[detected_footnote] = footnotes[footnote]

    return valid_footnotes


# Search for footnote in aanda entry and if found, add it to the json object the entry belongs to
def search_and_add_aanda_footnote_to_obj(footnotes, entry, json_obj):
    if not entry:
        return
    for footnote in footnotes:
        possible_footnote_value = footnote.replace("(", "").replace(")", "")
        if footnote in entry:
            json_obj["content"] = json_obj["content"].replace(f"{str(footnote)}", "")
            json_obj["note"] = footnotes[footnote]
            continue
        if possible_footnote_value in entry:
            json_obj["content"] = json_obj["content"].replace(
                f"{possible_footnote_value}", ""
            )
            json_obj["note"] = footnotes[footnote]


# Search for metadata in initial aanda
# journal (without table suffix)
def search_aanda_journal_metadata(journal):
    metadata = {}
    for aanda_file in list(title_to_metadata.keys()):
        if aanda_file.replace(".html", "") in journal:
            metadata = title_to_metadata[aanda_file]
    return metadata
