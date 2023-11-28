function checkPageQueryDisplay() {
    checkSearchTypeHeader();
    checkPlaceholders();
}

function checkSearchTypeHeader() {
    switch ("{{search_type}}") {
        case "title":
            document.getElementById("search-type-header").innerHTML = "Search By Title";
            break;
        case "author":
            document.getElementById("search-type-header").innerHTML = "Search By Author";
            break;
        case "year_range":
            document.getElementById("search-type-header").innerHTML = "Search By Year Range";
            break;
        case "year":
            document.getElementById("search-type-header").innerHTML = "Search By Year";
            break;
        case "journal":
            document.getElementById("search-type-header").innerHTML = "Search By Journal";
            break;
        case "table_caption":
            document.getElementById("search-type-header").innerHTML = "Search By Table Caption";
            break;
        case "word_in_table":
            document.getElementById("search-type-header").innerHTML = "Search By Word In Table";
            break;
        case "doi":
            document.getElementById("search-type-header").innerHTML = "Search By DOI";
            break;
        case "author_and_year":
            document.getElementById("search-type-header").innerHTML = "Search By Author & Year";
            break;
        case "author_and_journal":
            document.getElementById("search-type-header").innerHTML = "Search By Author & Journal";
            break;
    }
}

function checkPlaceholders() {
    if ("{{search_type}}" === "year_range") {
        document.getElementById("input_text").placeholder = "Enter start year...";
        document.getElementById("extra_input_text").placeholder = "Enter end year...";
    } else if ("{{search_type}}" === "table_caption") {
        document.getElementById("input_text").placeholder = "Enter table caption...";
    } else if ("{{search_type}}" === "word_in_table") {
        document.getElementById("input_text").placeholder = "Enter word in table...";
    } else if ("{{search_type}}" === "author_and_year") {
        document.getElementById("input_text").placeholder = "Enter author...";
        document.getElementById("extra_input_text").placeholder = "Enter year...";
    } else if ("{{search_type}}" === "author_and_journal") {
        document.getElementById("input_text").placeholder = "Enter author...";
        document.getElementById("extra_input_text").placeholder = "Enter journal...";
    }
}