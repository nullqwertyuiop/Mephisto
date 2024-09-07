import json
import re
from typing import Any

from avilla.core.elements import (
    Picture,
    Notice,
    NoticeAll,
    Audio,
    Video,
    File,
    Reference,
    Face,
)
from avilla.core.selector import Selector
from flywheel import SimpleOverload, FnCollectEndpoint, global_collect
from graia.amnesia.message.chain import MessageChain
from graia.amnesia.message.element import Element, Text

from mephisto.library.model.exception import MessageDeserializationFailed
from mephisto.library.util.message.resource import RecordAttachmentResource

ELEMENT_OVERLOAD = SimpleOverload("element")
RAW_TYPE_OVERLOAD = SimpleOverload("raw_type")


@FnCollectEndpoint
def impl_deserialize(raw_type: str, element: str):
    yield ELEMENT_OVERLOAD.hold(element)
    yield RAW_TYPE_OVERLOAD.hold(raw_type)

    def shape(raw_type: str, element: str, raw: Any) -> Element: ...  # noqa

    return shape


def deserialize_element(raw_type: str, element: str, raw: Any) -> Element:
    for selection in impl_deserialize.select():
        if not selection.harvest(ELEMENT_OVERLOAD, element) or not selection.harvest(
            RAW_TYPE_OVERLOAD, raw_type
        ):
            continue

        selection.complete()

    return selection(raw_type, element, raw)  # noqa


# Reserved for backward compatibility
# <editor-fold desc="Deserialize (repr)">
@global_collect
@impl_deserialize(raw_type="repr", element="Text")
def deserialize_repr_text(raw_type: str, element: str, raw: str) -> Text:
    pattern = r"(?P<element>Text)\(text=(?P<text>.+?)(?:, style=(?P<style>.+?))?\)"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return Text(match["text"], match["style"])


@global_collect
@impl_deserialize(raw_type="repr", element="Notice")
def deserialize_repr_notice(raw_type: str, element: str, raw: str) -> Notice:
    pattern = r"\[\$?(?P<element>Notice):target=(?P<target>.+?)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return Notice(
        Selector.from_follows(match["target"].split("Selector().")[-1]),
    )


@global_collect
@impl_deserialize(raw_type="repr", element="NoticeAll")
def deserialize_repr_notice_all(raw_type: str, element: str, raw: str) -> NoticeAll:
    return NoticeAll()


@global_collect
@impl_deserialize(raw_type="repr", element="Picture")
def deserialize_repr_picture(raw_type: str, element: str, raw: str) -> Picture:
    pattern = r"\[\$?(?P<element>Picture):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return Picture(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Audio")
def deserialize_repr_audio(raw_type: str, element: str, raw: str) -> Audio:
    pattern = r"\[\$?(?P<element>Audio):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return Audio(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Video")
def deserialize_repr_video(raw_type: str, element: str, raw: str) -> Video:
    pattern = r"\[\$?(?P<element>Video):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return Video(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="File")
def deserialize_repr_file(raw_type: str, element: str, raw: str) -> File:
    pattern = r"\[\$?(?P<element>File):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return File(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Reference")
def deserialize_repr_reference(raw_type: str, element: str, raw: str) -> Reference:
    pattern = r"\[\$?(?P<element>Reference):id=(?P<message>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return Reference(
        Selector.from_follows(match["message"]),
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Face")
def deserialize_repr_face(raw_type: str, element: str, raw: str) -> Face:
    pattern = r"\[\$?(?P<element>Face):id=(?P<id>.+);name=(?P<name>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return Face(
        match["id"],
        match["name"] if match["name"] != "None" else None,
    )


def deserialize_repr(raw: str) -> MessageChain:
    raw = raw[14:-2] + ", "  # MessageChain([...])
    combined_pattern = re.compile(
        r"(?:\[\$?)?(?P<element>[a-zA-Z]+)(?:[:(].+?[)\]])?, "
    )
    chain = []
    while raw:
        match = combined_pattern.match(raw)
        if not match:
            raise MessageDeserializationFailed(raw=raw)
        element = match["element"]
        raw = raw[match.end() :]
        chain.append(deserialize_element("repr", element, match.group(0)))
    return MessageChain(chain)


# </editor-fold>


# <editor-fold desc="Deserialize (json)">
@global_collect
@impl_deserialize(raw_type="json", element="Text")
def deserialize_json_text(raw_type: str, element: str, raw: dict[str, Any]) -> Text:
    return Text(raw["text"], style=raw.get("style"))


@global_collect
@impl_deserialize(raw_type="json", element="Notice")
def deserialize_json_notice(raw_type: str, element: str, raw: dict[str, Any]) -> Notice:
    return Notice(Selector.from_follows(raw["target"]), display=raw.get("display"))


@global_collect
@impl_deserialize(raw_type="json", element="NoticeAll")
def deserialize_json_notice_all(
    raw_type: str, element: str, raw: dict[str, Any]
) -> NoticeAll:
    return NoticeAll()


@global_collect
@impl_deserialize(raw_type="json", element="Picture")
def deserialize_json_picture(
    raw_type: str, element: str, raw: dict[str, Any]
) -> Picture:
    return Picture(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
    )


@global_collect
@impl_deserialize(raw_type="json", element="Audio")
def deserialize_json_audio(raw_type: str, element: str, raw: dict[str, Any]) -> Audio:
    return Audio(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
        duration=raw.get("duration"),
    )


@global_collect
@impl_deserialize(raw_type="json", element="Video")
def deserialize_json_video(raw_type: str, element: str, raw: dict[str, Any]) -> Video:
    return Video(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
    )


@global_collect
@impl_deserialize(raw_type="json", element="File")
def deserialize_json_file(raw_type: str, element: str, raw: dict[str, Any]) -> File:
    return File(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
    )


@global_collect
@impl_deserialize(raw_type="json", element="Reference")
def deserialize_json_reference(
    raw_type: str, element: str, raw: dict[str, Any]
) -> Reference:
    if ref_slice := raw.get("slice"):
        if (
            len(ref_slice) == 2
            and isinstance(ref_slice[0], int)
            and isinstance(ref_slice[1], int)
        ):
            return Reference(
                Selector.from_follows(raw["resource"]),
                slice=(ref_slice[0], ref_slice[1]),
            )
    return Reference(Selector.from_follows(raw["resource"]), slice=None)


@global_collect
@impl_deserialize(raw_type="json", element="Face")
def deserialize_json_face(raw_type: str, element: str, raw: dict[str, Any]) -> Face:
    return Face(raw["id"], name=raw.get("name"))


def deserialize_json(raw: str) -> MessageChain:
    raw = raw[5:]  # json:[{...}]
    data: list[dict[str, Any]] = json.loads(raw)
    chain = [deserialize_element("json", element["_type"], element) for element in data]
    return MessageChain(chain)


# </editor-fold>


def deserialize(raw: str) -> MessageChain:
    if raw.startswith("json:"):
        return deserialize_json(raw)
    elif raw.startswith("MessageChain"):
        return deserialize_repr(raw)
    else:
        raise MessageDeserializationFailed(raw=raw)
