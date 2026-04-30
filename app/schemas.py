from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.constants import email_length, image_file_length, title_length, username_length


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=username_length)
    email: EmailStr = Field(max_length=email_length)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=username_length)
    email: EmailStr | None = Field(default=None, max_length=email_length)
    image_file: str | None = Field(
        default=None, min_length=1, max_length=image_file_length
    )


class UserResponse(UserBase):
    model_config = ConfigDict(  # pyright: ignore[reportUnannotatedClassAttribute]
        from_attributes=True
    )

    id: int
    image_file: str | None
    image_path: str


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
    author: UserResponse
