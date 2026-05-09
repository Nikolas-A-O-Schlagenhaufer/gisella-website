from datetime import UTC, datetime, timedelta
from typing import Annotated, override
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash
from sqlalchemy import select

from app.config import settings
from app.db import DataBase
import app.models as models


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    @override
    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        if authorization:
            return await super().__call__(request)
        token = request.cookies.get("access_token")
        if token:
            return token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Token não foi encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )


password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="api/user/token")


def hash_password(password: str) -> str:
    """
    Executa um hash na senha passada como argumento.
    """
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Compara a senha passada com a senha com hash passada.
    """
    return password_hasher.verify(password, hashed_password)


def create_access_token(
    data: dict,  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    expires_delta: timedelta | None = None,
) -> str:
    """
    Cria um token de acesso JWT.
    """
    to_encode = data.copy()  # pyright: ignore[reportUnknownVariableType]
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})  # pyright: ignore[reportUnknownMemberType]
    encoded_jwt = jwt.encode(  # pyright: ignore[reportUnknownMemberType]
        to_encode,  # pyright: ignore[reportUnknownArgumentType]
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorith,
    )
    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    """
    Verifica um token de acesso JWT e retorna o sujeito (id do usuário) caso o token seja válido.
    """
    try:
        payload = jwt.decode(  # pyright: ignore[reportUnknownMemberType]
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorith],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DataBase
) -> models.User:
    user_id_str = verify_access_token(token)
    if not user_id_str:
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
            detail="usuário não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[models.User, Depends(get_current_user)]
