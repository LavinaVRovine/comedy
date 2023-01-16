import json
from abc import ABC
from dataclasses import dataclass, asdict
from datetime import date, datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.fromisoformat(value)
            #json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except:
            pass
    return json_dict

@dataclass
class Content(ABC):
    id: str

    def __new__(cls, *args, **kwargs):
        if cls == Content:
            raise TypeError("Cannot instantiate abstract class.")
        return super().__new__(cls)

    def encode(self):
        return json.dumps(
            self.as_dict(), cls=DateTimeEncoder
        )

    def as_dict(self):
        return asdict(self)

    @staticmethod
    def _dump_v(v):
        if isinstance(v, datetime):

            format_ = "yyyy-MM-ddTHH:mm:ss"
            return v.strftime(format_)
        return v

    @classmethod
    def to_avro(cls, obj, ctx) -> dict:
        return {k.upper(): obj._dump_v(v) for k, v in obj.as_dict().items()}

    @classmethod
    def decode(cls, value: str) -> dict:
        v = json.loads(
            value, object_hook=date_hook
        )
        return v

    @classmethod
    def from_avro(cls, value: dict, ctx):
        if not value:
            return
        #value["_id"] = "lala"
        #value["thumbnails"] = {}
        return cls(
            **{k.lower(): v for k, v in value.items()}
        )

    @classmethod
    def make_instance_of_self(cls, value: str, ):

        return cls(
            **cls.decode(value)
        )

