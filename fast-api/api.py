import sys
import json

sys.path.append("../table-extracts")
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from elastic_index import (
    search_index_by_author,
    search_index_by_year,
    search_index_by_year_range,
    search_index_by_journal,
    search_index_by_title,
    search_index_by_table_caption,
    search_index_by_word_in_table,
    search_index_by_doi_all,
    search_index_by_author_and_year,
    search_index_by_author_and_journal,
    search_index_by_journal_and_year,
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, search_type: str):
    return templates.TemplateResponse(
        "query.html", {"request": request, "search_type": search_type}
    )


@app.get("/query", response_class=HTMLResponse)
async def query(
    request: Request,
    input_search: str,
    search_type: str,
    extra_input_search: str = None,
):
    results = None
    index_name = "astro"
    match search_type:
        case "title":
            results = search_index_by_title(input_search, index_name)
        case "author":
            results = search_index_by_author(input_search, index_name)
        case "year_range":
            results = search_index_by_year_range(
                input_search, extra_input_search, index_name
            )
        case "year":
            results = search_index_by_year(input_search, index_name)
        case "journal":
            results = search_index_by_journal(input_search, index_name)
        case "table_caption":
            results = search_index_by_table_caption(input_search, index_name)
        case "word_in_table":
            results = search_index_by_word_in_table(index_name, input_search)
        case "doi":
            results = search_index_by_doi_all(input_search)
        case "author_and_year":
            results = search_index_by_author_and_year(
                input_search, extra_input_search, index_name
            )
        case "author_and_journal":
            results = search_index_by_author_and_journal(
                extra_input_search, input_search, index_name
            )
        case "journal_and_year":
            results = search_index_by_journal_and_year(
                input_search, extra_input_search, index_name
            )

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "input_search": input_search,
            "extra_input_search": extra_input_search,
            "search_type": search_type,
            "results": results,
        },
    )
