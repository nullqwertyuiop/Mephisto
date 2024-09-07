import json
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
from flywheel import SimpleOverload, FnCollectEndpoint, global_collect, TypeOverload
from graia.amnesia.message.chain import MessageChain
from graia.amnesia.message.element import Element, Text

RAW_TYPE_OVERLOAD = SimpleOverload("raw_type")
ELEMENT_OVERLOAD = TypeOverload("element")


@FnCollectEndpoint
def impl_serialize(raw_type: str, element: type[Element]):
    yield RAW_TYPE_OVERLOAD.hold(raw_type)
    yield ELEMENT_OVERLOAD.hold(element)

    def shape(raw_type: str, element: Element) -> dict[str, Any]: ...  # noqa

    return shape


def serialize_element(raw_type: str, element: Element) -> dict[str, Any]:
    for selection in impl_serialize.select():
        if not selection.harvest(RAW_TYPE_OVERLOAD, raw_type) or not selection.harvest(
            ELEMENT_OVERLOAD, element
        ):
            continue

        selection.complete()

    return selection(raw_type, element)  # noqa


# <editor-fold desc="Serialize (json)">
@global_collect
@impl_serialize(raw_type="json", element=Text)
def serialize_json_text(raw_type: str, element: Text) -> dict:
    return {"_type": "Text", "text": element.text, "style": element.style}


@global_collect
@impl_serialize(raw_type="json", element=Notice)
def serialize_json_notice(raw_type: str, element: Notice) -> dict:
    return {
        "_type": "Notice",
        "target": element.target.display,
        "display": element.display,
    }


@global_collect
@impl_serialize(raw_type="json", element=NoticeAll)
def serialize_json_notice_all(raw_type: str, element: NoticeAll) -> dict:
    return {"_type": "NoticeAll"}


@global_collect
@impl_serialize(raw_type="json", element=Picture)
def serialize_json_picture(raw_type: str, element: Picture) -> dict:
    return {"_type": "Picture", "resource": element.resource.to_selector().display}


@global_collect
@impl_serialize(raw_type="json", element=Audio)
def serialize_json_audio(raw_type: str, element: Audio) -> dict:
    return {
        "_type": "Audio",
        "resource": element.resource.to_selector().display,
        "duration": element.duration,
    }


@global_collect
@impl_serialize(raw_type="json", element=Video)
def serialize_json_video(raw_type: str, element: Video) -> dict:
    return {"_type": "Video", "resource": element.resource.to_selector().display}


@global_collect
@impl_serialize(raw_type="json", element=File)
def serialize_json_file(raw_type: str, element: File) -> dict:
    return {"_type": "File", "resource": element.resource.to_selector().display}


@global_collect
@impl_serialize(raw_type="json", element=Reference)
def serialize_json_reference(raw_type: str, element: Reference) -> dict:
    return {
        "_type": "Reference",
        "resource": element.message.to_selector().display,
        "slice": list(element.slice),
    }


@global_collect
@impl_serialize(raw_type="json", element=Face)
def serialize_json_face(raw_type: str, element: Face) -> dict:
    return {"_type": "Face", "id": element.id, "name": element.name}


# </editor-fold>


def serialize(chain: MessageChain) -> str:
    return "json:" + json.dumps(
        [serialize_element("json", element) for element in chain]
    )
