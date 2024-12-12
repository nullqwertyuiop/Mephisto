from dataclasses import dataclass
from typing import Any

from flywheel import FnCollectEndpoint, TypeOverload
from graia.amnesia.message.element import Element

from mephisto.library.model.metadata import StandardMetadata

_DATA_TYPE_OVERLOAD = TypeOverload("data")


@dataclass
class ModerationResult:
    data: str | Element
    result: dict[str, Any]


@FnCollectEndpoint
def impl_moderation(data_type: type[str | Element]):
    yield _DATA_TYPE_OVERLOAD.hold(data_type)

    def shape(data: str | Element) -> ModerationResult: ...

    return shape


def moderate(data: str | Element) -> ModerationResult:
    for selection in impl_moderation.select():
        if not selection.harvest(_DATA_TYPE_OVERLOAD, data):
            continue
        selection.complete()
        return selection(data)
    return ModerationResult(data, {})


def export() -> StandardMetadata:
    return StandardMetadata(
        identifier="library.standard.moderation",
        name="Moderation",
        version="0.0.1",
        description="A standard for moderation",
    )
