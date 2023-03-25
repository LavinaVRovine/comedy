from pydantic import BaseModel


class SourceBase(BaseModel):
    ...

class SourceUpdate(SourceBase):
    ...