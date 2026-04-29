from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

templates = Jinja2Templates(directory="app/templates")

posts: list[dict[str, str | int]] = [
    {
        "id": 1,
        "author": "Nikolas Schlagenhaufer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use.",
        "date_posted": "29/04/2026",
    },
    {
        "id": 2,
        "author": "Gabriel Schlagenhaufer",
        "title": "FastAPI is not Awesome",
        "content": "This framework is not really easy to use.",
        "date_posted": "30/04/2026",
    },
]


@app.get("/", include_in_schema=False, name="home")
@app.get("/post", include_in_schema=False, name="post")
def home(request: Request):
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Home"}
    )


@app.get("/api/post")
def get_post():
    return posts
