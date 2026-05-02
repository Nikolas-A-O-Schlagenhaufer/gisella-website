from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db import Base, engine
from app.dependencies import templates
from app.routers import page as page_routes, user as user_routes, post as post_routes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
app.mount("/media", StaticFiles(directory="app/media", html=True), name="media")

app.include_router(page_routes.router, prefix="", tags=["Página"])
app.include_router(post_routes.router, prefix="/api/post", tags=["Postagem"])
app.include_router(user_routes.router, prefix="/api/user", tags=["Usuário"])


## Exception Handlers --------------------------------------------------------------------


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request, exception: StarletteHTTPException
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
    message = (
        exception.detail
        if exception.detail
        else "Ocorreu um erro. Favor checar a sua requisição e tentar novamente."
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
async def validation_exception_handler(
    request: Request, exception: RequestValidationError
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
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
