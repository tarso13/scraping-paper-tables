from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
async def query(request: Request, input_search: str):
    return templates.TemplateResponse(
        "result.html", {"request": request, "input_search": input_search}
    )
