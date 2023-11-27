import sys

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


@app.get("/favicon.ico", response_class=HTMLResponse)
async def favicon():
    return HTMLResponse(content="", status_code=404)


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
    match search_type:
        case "title":
            results = search_index_by_title(input_search)
        case "author":
            results = search_index_by_author(input_search)
        case "year_range":
            start_year = input_search
            end_year = extra_input_search
            results = search_index_by_year_range(start_year, end_year)
        case "year":
            results = search_index_by_year(input_search)
        case "journal":
            results = search_index_by_journal(input_search)
        case "table_caption":
            results = search_index_by_table_caption(input_search)
        case "word_in_table":
            index_name = "astro"
            results = search_index_by_word_in_table(index_name, input_search)

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
