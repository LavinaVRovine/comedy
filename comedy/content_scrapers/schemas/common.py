from pydantic import BaseModel


class ImageNoSize(BaseModel):
    url: str


class Image(ImageNoSize):
    width: int
    height: int

    class Config:
        use_enum_values = True
        orm_mode = True


class Tag(BaseModel):
    key: str
    url: str
    description: str | None
    isSensitive: int | None