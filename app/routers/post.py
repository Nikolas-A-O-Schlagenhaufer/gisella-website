from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import CurrentUser
import app.models as models
from app.db import DataBase
from app.schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: DataBase, current_user: CurrentUser):
    """
    Criar uma nova postagem.
    """
    new_post = models.Post(
        title=post.title, content=post.content, user_id=current_user.id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post


@router.get("", response_model=list[PostResponse])
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


@router.get("/{post_id}", response_model=PostResponse)
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


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int, post_data: PostUpdate, db: DataBase, current_user: CurrentUser
):
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
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a atualizar as informações dessa postagem.",
        )
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():  # pyright: ignore[reportAny]
        setattr(post, field, value)
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: DataBase, current_user: CurrentUser):
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
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a remover essa postagem.",
        )
    await db.delete(post)
    await db.commit()
