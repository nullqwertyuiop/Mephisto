from dataclasses import is_dataclass
from typing import TypeVar, cast

from avilla.core import Resource, Context, Selector
from loguru import logger

OBJECT_IS_SELECTOR = "__object_is_selector__"

_T = TypeVar("_T")


class Attachment:
    context: Context | None
    resource: Resource | None

    def __init__(self, ctx: Context | None, res: Resource | None):
        self.context = self.parse(ctx) if ctx else None
        self.resource = self.parse(res) if res else None

    def parse(self, obj: _T) -> _T:
        if isinstance(obj, Selector):
            return cast(_T, {"pattern": dict(obj.pattern), OBJECT_IS_SELECTOR: True})
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif isinstance(obj, (list, tuple, set, frozenset)):
            return type(obj)(self.parse(item) for item in obj)
        elif isinstance(obj, (dict,)):
            return cast(_T, {__k: self.parse(__v) for __k, __v in obj.items()})
        elif is_dataclass(obj):
            for key in obj.__dict__:
                obj.__dict__[key] = self.parse(obj.__dict__[key])
            return obj
        logger.warning(f"[Attachment] Unhandled type: {type(obj)}")
        return obj

    def to_resource(self) -> Resource:
        if not self.resource:
            raise ValueError("[Attachment] No available resource to unparse")
