from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

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


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Página Inicial"}
    )


@app.get("/post/{post_id}", include_in_schema=False)
def post(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            post_title = (
                str(post.get("title"))
                if post.get("title") is not None and type(post.get("title")) == str
                else "Postagem"
            )
            return templates.TemplateResponse(
                request, "post.html", {"post": post, "title": post_title[:50]}
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
    )


@app.get("/api/post")
def get_posts():
    return posts


@app.get("/api/post/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
    )


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "Ocorreu um erro. Favor checar a sua requisição e tentar novamente."
    )
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code, content={"detail": message}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Requisição inválida. Favore checar os seus dados e tentar novamente.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
