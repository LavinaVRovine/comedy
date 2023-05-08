from pydantic import BaseModel


class ImageNoSize(BaseModel):
    url: str


class Image(ImageNoSize):
    width: int
    height: int

    class Config:
        use_enum_values = True
        orm_mode = True

class Topic(BaseModel):
    key: str
    url: str
class Tag(Topic):

    description: str | None
    isSensitive: int | None