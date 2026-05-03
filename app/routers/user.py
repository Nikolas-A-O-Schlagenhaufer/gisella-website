from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.auth import (
    create_access_token,  # pyright: ignore[reportUnknownVariableType]
    hash_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
)
from app.config import settings
from app.db import DataBase
import app.models as models
from app.schemas import (
    PostResponse,
    Token,
    UserCreate,
    UserUpdate,
    UserPublic,
    UserPrivate,
)

router = APIRouter()


@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: DataBase):
    """
    Criar um novo usuário.
    """
    existing_user_query = (
        select(models.User)
        .where(func.lower(models.User.username) == user.username.lower())
        .limit(1)
    )
    existing_user_result = await db.execute(existing_user_query)
    existing_user = existing_user_result.scalar()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nome de usuário já existe."
        )
    existing_email_query = (
        select(models.User)
        .where(func.lower(models.User.email) == user.email.lower())
        .limit(1)
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
        email=user.email.lower(),
        password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DataBase,
):
    """
    Cria o token de acesso para o usuário (faz o login do usuário).
    """
    user_query = (
        select(models.User)
        .where(func.lower(models.User.email) == form_data.username.lower())
        .limit(1)
    )
    user_result = await db.execute(user_query)
    user = user_result.scalar()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
        secure=True,
        httponly=True,
        samesite="lax",
    )
    return Token(access_token=access_token, toke_type="bearer")


@router.get("/me", response_model=UserPrivate)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DataBase):
    """
    Retorna o usuário logado atualmente.
    """
    user_id_str = verify_access_token(token)
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = int(user_id_str)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_query = select(models.User).where(models.User.id == user_id).limit(1)
    user_result = await db.execute(user_query)
    user = user_result.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.get(
    "/logout", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND
)
async def logout_user():
    """
    Deslogar um usuário.
    """
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key="access_token",
        secure=True,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/{user_id}", response_model=UserPublic)
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


@router.patch("/{user_id}", response_model=UserPrivate)
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
    if (
        user_data.username is not None
        and user_data.username.lower() != user.username.lower()
    ):
        existing_user_query = (
            select(models.User)
            .where(func.lower(models.User.username) == user_data.username.lower())
            .limit(1)
        )
        existing_user_result = await db.execute(existing_user_query)
        existing_user = existing_user_result.scalar()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário já existe.",
            )
    if user_data.email is not None and user_data.email.lower() != user.email.lower():
        existing_email_query = (
            select(models.User)
            .where(func.lower(models.User.email) == user_data.email.lower())
            .limit(1)
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
        user.email = user_data.email.lower()
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
