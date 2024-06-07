from dataclasses import is_dataclass
from typing import Any

from avilla.core import Resource, Context, Selector
from loguru import logger

OBJECT_IS_SELECTOR = "__object_is_selector__"
OBJECT_MODULE = "__object_module__"
OBJECT_CLASS = "__object_class__"


class Attachment:
    attachment: dict[str, Any]
    account_pattern: dict[str, str]

    def __init__(self, ctx: Context | None, res: Resource | None):
        if res:
            self.attachment = self.parse_dataclass(res)
            self.attachment[OBJECT_MODULE] = res.__class__.__module__
            self.attachment[OBJECT_CLASS] = res.__class__.__qualname__
        else:
            self.attachment = {}

        self.account_pattern = dict(ctx.account.route.pattern) if ctx else {}

    @staticmethod
    def parse_dataclass(cls_obj) -> dict[str, Any]:
        pickleable_types = (int, float, str, bool, type(None))
        iterables = (list, tuple, set, frozenset)
        dict_types = (dict,)

        def parse(obj):
            if isinstance(obj, Selector):
                obj = dict(obj.pattern)
                obj[OBJECT_IS_SELECTOR] = "1"
            if isinstance(obj, pickleable_types):
                return obj
            if isinstance(obj, iterables):
                return [parse(item) for item in obj]
            if isinstance(obj, dict_types):
                return {key: parse(value) for key, value in obj.items()}
            if is_dataclass(obj):
                parsed = {key: parse(value) for key, value in obj.__dict__.items()}
                parsed[OBJECT_MODULE] = obj.__class__.__module__
                parsed[OBJECT_CLASS] = obj.__class__.__qualname__
                return parsed
            logger.warning(f"[Attachment] Unhandled type: {type(obj)}")

        return {key: parse(value) for key, value in cls_obj.__dict__.items()}

    def to_resource(self):
        raise NotImplementedError
