from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/post", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{posts[0]["title"]}</h1>"


@app.get("/api/post")
def get_post():
    return posts
