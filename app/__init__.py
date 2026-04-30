from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas import PostCreate, PostResponse, UserCreate, UserResponse
from app.db import Base, DataBase, engine
import app.models as models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
app.mount("/media", StaticFiles(directory="app/media", html=True), name="media")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", include_in_schema=False)
def home(request: Request, db: DataBase):
    posts_query = select(models.Post).order_by(models.Post.date_posted.desc())
    posts = db.execute(posts_query).scalars().all()
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Página Inicial"}
    )


@app.get("/post/{post_id}", include_in_schema=False)
def post(request: Request, post_id: int, db: DataBase):
    post_query = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .order_by(models.Post.date_posted.desc())
        .limit(1)
    )
    post = db.execute(post_query).scalar()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
        )
    return templates.TemplateResponse(
        request, "post.html", {"post": post, "title": post.title[:50]}
    )


@app.get("/user/{user_id}/post", include_in_schema=False)
def user_post(request: Request, user_id: int, db: DataBase):
    user_query = select(models.User).where(models.User.id == user_id).limit(1)
    user = db.execute(user_query).scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    user_posts_query = (
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
    )
    user_posts = db.execute(user_posts_query).scalars().all()
    return templates.TemplateResponse(
        request,
        "user_post.html",
        {"posts": user_posts, "user": user, "title": f"Postagens de {user.username}"},
    )


@app.post("/api/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DataBase):
    existing_user_query = (
        select(models.User).where(models.User.username == user.username).limit(1)
    )
    existing_user = db.execute(existing_user_query).scalar()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nome de usuário já existe."
        )
    existing_email_query = (
        select(models.User).where(models.User.email == user.email).limit(1)
    )
    existing_email = db.execute(existing_email_query).scalar()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está sendo utilizado.",
        )
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DataBase):
    existing_user_query = select(models.User).where(models.User.id == user_id).limit(1)
    existing_user = db.execute(existing_user_query).scalar()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    return existing_user


@app.get("/api/user/{user_id}/post", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: DataBase):
    user_query = select(models.User).where(models.User.id == user_id).limit(1)
    user = db.execute(user_query).scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    user_posts_query = (
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
    )
    user_posts = db.execute(user_posts_query).scalars().all()
    return user_posts


@app.post("/api/post", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: DataBase):
    user_query = select(models.User).where(models.User.id == post.user_id).limit(1)
    user = db.execute(user_query).scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/api/post", response_model=list[PostResponse])
def get_posts(db: DataBase):
    posts_query = select(models.Post).order_by(models.Post.date_posted.desc())
    posts = db.execute(posts_query).scalars().all()
    return posts


@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: DataBase):
    post_query = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .order_by(models.Post.date_posted.desc())
        .limit(1)
    )
    post = db.execute(post_query).scalar()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
        )
    return post


## Exception Handlers --------------------------------------------------------------------


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
