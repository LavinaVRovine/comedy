from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    def to_orm_json(self, *args, **kwargs):
        return self.dict(*args, **kwargs)
