from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import DataBase
import app.models as models
from app.schemas import PostResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("/{user_id}", response_model=UserResponse)
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


@router.get("/{user_id}/post", response_model=list[PostResponse])
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


@router.patch("/{user_id}", response_model=UserResponse)
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
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
