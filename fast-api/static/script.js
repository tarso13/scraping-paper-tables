function checkPageQueryDisplay() {
    var currentURL = window.location.href;
    var url = new URL(currentURL);
    var search_type = url.searchParams.get('search_type');
    checkSearchTypeHeader(search_type);
    checkPlaceholders(search_type);
}

function checkSearchTypeHeader(search_type) {
    switch (search_type) {
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
        case "journal_and_year":
            document.getElementById("search-type-header").innerHTML = "Search By Journal & Year";
            break;
    }
}

function checkPlaceholders(search_type) {
    switch (search_type) {
        case "year_range":
            document.getElementById("input_text").placeholder = "Enter start year...";
            document.getElementById("extra_input_text").placeholder = "Enter end year...";
            break;
        case "table_caption":
            document.getElementById("input_text").placeholder = "Enter table caption...";
            break;
        case "word_in_table":
            document.getElementById("input_text").placeholder = "Enter word in table...";
            break;
        case "author_and_year":
            document.getElementById("input_text").placeholder = "Enter author...";
            document.getElementById("extra_input_text").placeholder = "Enter year...";
            break;
        case "author_and_journal":
            document.getElementById("input_text").placeholder = "Enter author...";
            document.getElementById("extra_input_text").placeholder = "Enter journal...";
            break;
        case "journal_and_year":
            document.getElementById("input_text").placeholder = "Enter journal...";
            document.getElementById("extra_input_text").placeholder = "Enter year...";
            break;
    }
}
