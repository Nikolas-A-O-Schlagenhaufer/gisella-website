from datetime import UTC, datetime, timedelta
from typing import override
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash

from app.config import settings


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
