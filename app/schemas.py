from pydantic import BaseModel, ConfigDict, Field


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=255)


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    model_config = ConfigDict(  # pyright: ignore[reportUnannotatedClassAttribute]
        from_attributes=True
    )

    id: int
    date_posted: str
