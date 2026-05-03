from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.constants import email_length, image_file_length, title_length, username_length


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=username_length)
    email: EmailStr = Field(max_length=email_length)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=username_length)
    email: EmailStr | None = Field(default=None, max_length=email_length)
    image_file: str | None = Field(
        default=None, min_length=1, max_length=image_file_length
    )


class UserPublic(BaseModel):
    model_config = ConfigDict(  # pyright: ignore[reportUnannotatedClassAttribute]
        from_attributes=True
    )

    id: int
    username: str
    image_file: str | None
    image_path: str


class UserPrivate(UserPublic):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    toke_type: str


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=title_length)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    user_id: int


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=title_length)
    content: str | None = Field(default=None, min_length=1)


class PostResponse(PostBase):
    model_config = ConfigDict(  # pyright: ignore[reportUnannotatedClassAttribute]
        from_attributes=True
    )

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic
