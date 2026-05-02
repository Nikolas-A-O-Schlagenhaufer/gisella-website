from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies import templates
import app.models as models
from app.db import DataBase

router = APIRouter()


@router.get("/", include_in_schema=False)
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


@router.get("/post/{post_id}", include_in_schema=False)
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


@router.get("/user/{user_id}/post", include_in_schema=False)
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
