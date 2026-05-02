from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db import Base, DataBase, engine
import app.models as models
from app.schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
app.mount("/media", StaticFiles(directory="app/media", html=True), name="media")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", include_in_schema=False)
async def home(request: Request, db: DataBase):
    """
    Página inicial
    """
    posts_query = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
    )
    posts_result = await db.execute(posts_query)
    posts = posts_result.scalars().all()
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Página Inicial"}
    )


@app.get("/post/{post_id}", include_in_schema=False)
async def post(request: Request, post_id: int, db: DataBase):
    """
    Página de uma postagem.
    """
    post_query = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .limit(1)
    )
    post_result = await db.execute(post_query)
    post = post_result.scalar()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
        )
    return templates.TemplateResponse(
        request, "post.html", {"post": post, "title": post.title[:50]}
    )


@app.get("/user/{user_id}/post", include_in_schema=False)
async def user_post(request: Request, user_id: int, db: DataBase):
    """
    Página das postagens de um usuário.
    """
    user_query = select(models.User).where(models.User.id == user_id).limit(1)
    user_result = await db.execute(user_query)
    user = user_result.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    user_posts_query = (
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
    )
    user_posts_result = await db.execute(user_posts_query)
    user_posts = user_posts_result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_post.html",
        {"posts": user_posts, "user": user, "title": f"Postagens de {user.username}"},
    )


@app.post("/api/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: DataBase):
    """
    Criar um novo usuário.
    """
    existing_user_query = (
        select(models.User).where(models.User.username == user.username).limit(1)
    )
    existing_user_result = await db.execute(existing_user_query)
    existing_user = existing_user_result.scalar()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nome de usuário já existe."
        )
    existing_email_query = (
        select(models.User).where(models.User.email == user.email).limit(1)
    )
    existing_email_result = await db.execute(existing_email_query)
    existing_email = existing_email_result.scalar()
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
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.get("/api/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: DataBase):
    """
    Obter dados de um usuário.
    """
    existing_user_query = select(models.User).where(models.User.id == user_id).limit(1)
    existing_user_result = await db.execute(existing_user_query)
    existing_user = existing_user_result.scalar()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    return existing_user


@app.get("/api/user/{user_id}/post", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: DataBase):
    """
    Obter dados das postagens de um usuário.
    """
    user_query = select(models.User).where(models.User.id == user_id).limit(1)
    user_result = await db.execute(user_query)
    user = user_result.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    user_posts_query = (
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
    )
    user_posts_result = await db.execute(user_posts_query)
    user_posts = user_posts_result.scalars().all()
    return user_posts


@app.patch("/api/user/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: DataBase):
    """
    Atualizar campos de um usuário.
    """
    user_query = select(models.User).where(models.User.id == user_id).limit(1)
    user_result = await db.execute(user_query)
    user = user_result.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    if user_data.username is not None and user_data.username != user.username:
        existing_user_query = (
            select(models.User)
            .where(models.User.username == user_data.username)
            .limit(1)
        )
        existing_user_result = await db.execute(existing_user_query)
        existing_user = existing_user_result.scalar()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário já existe.",
            )
    if user_data.email is not None and user_data.email != user.email:
        existing_email_query = (
            select(models.User).where(models.User.email == user_data.email).limit(1)
        )
        existing_email_result = await db.execute(existing_email_query)
        existing_email = existing_email_result.scalar()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está sendo utilizado.",
            )
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.image_file is not None:
        user.image_file = user_data.image_file
    await db.commit()
    await db.refresh(user)
    return user


@app.delete("/api/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DataBase):
    """
    Remover um usuário.
    """
    user_query = select(models.User).where(models.User.id == user_id).limit(1)
    user_result = await db.execute(user_query)
    user = user_result.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    await db.delete(user)
    await db.commit()


@app.post("/api/post", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: DataBase):
    """
    Criar uma nova postagem.
    """
    user_query = select(models.User).where(models.User.id == post.user_id).limit(1)
    user_result = await db.execute(user_query)
    user = user_result.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post


@app.get("/api/post", response_model=list[PostResponse])
async def get_posts(db: DataBase):
    """
    Obter dados de todas as postagens.
    """
    posts_query = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
    )
    posts_result = await db.execute(posts_query)
    posts = posts_result.scalars().all()
    return posts


@app.get("/api/post/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: DataBase):
    """
    Obter dados de uma postagem.
    """
    post_query = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .limit(1)
    )
    post_result = await db.execute(post_query)
    post = post_result.scalar()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
        )
    return post


@app.patch("/api/post/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostUpdate, db: DataBase):
    """
    Atualizar campos de uma postagem.
    """
    post_query = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
        .limit(1)
    )
    post_result = await db.execute(post_query)
    post = post_result.scalar()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
        )
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():  # pyright: ignore[reportAny]
        setattr(post, field, value)
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@app.delete("/api/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: DataBase):
    """
    Remover uma postagem.
    """
    post_query = select(models.Post).where(models.Post.id == post_id).limit(1)
    post_result = await db.execute(post_query)
    post = post_result.scalar()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postagem não encontrada."
        )
    await db.delete(post)
    await db.commit()


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
