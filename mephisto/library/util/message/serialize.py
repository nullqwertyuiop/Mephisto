import json
from typing import Any

from avilla.core.elements import Audio as CoreAudio
from avilla.core.elements import Face as CoreFace
from avilla.core.elements import File as CoreFile
from avilla.core.elements import Notice as CoreNotice
from avilla.core.elements import NoticeAll as CoreNoticeAll
from avilla.core.elements import Picture as CorePicture
from avilla.core.elements import Reference as CoreReference
from avilla.core.elements import Text as CoreText
from avilla.core.elements import Video as CoreVideo
from avilla.standard.qq.elements import App as QqApp
from avilla.standard.qq.elements import Dice as QqDice
from avilla.standard.qq.elements import FlashImage as QqFlashImage
from avilla.standard.qq.elements import Forward as QqForward
from avilla.standard.qq.elements import Gift as QqGift
from avilla.standard.qq.elements import Json as QqJson
from avilla.standard.qq.elements import MarketFace as QqMarketFace
from avilla.standard.qq.elements import MusicShare as QqMusicShare
from avilla.standard.qq.elements import Poke as QqPoke
from avilla.standard.qq.elements import Share as QqShare
from avilla.standard.qq.elements import Xml as QqXml
from avilla.standard.telegram.elements import Animation as TgAnimation
from avilla.standard.telegram.elements import Contact as TgContact
from avilla.standard.telegram.elements import Dice as TgDice
from avilla.standard.telegram.elements import Location as TgLocation
from avilla.standard.telegram.elements import Picture as TgPicture
from avilla.standard.telegram.elements import Sticker as TgSticker
from avilla.standard.telegram.elements import Story as TgStory
from avilla.standard.telegram.elements import Venue as TgVenue
from avilla.standard.telegram.elements import Video as TgVideo
from avilla.standard.telegram.elements import VideoNote as TgVideoNote
from flywheel import FnCollectEndpoint, SimpleOverload, TypeOverload, global_collect
from graia.amnesia.message.chain import MessageChain
from graia.amnesia.message.element import Element

_RAW_TYPE_OVERLOAD = SimpleOverload("raw_type")
_ELEMENT_OVERLOAD = TypeOverload("element")


@FnCollectEndpoint
def impl_serialize(raw_type: str, element: type[Element]):
    yield _RAW_TYPE_OVERLOAD.hold(raw_type)
    yield _ELEMENT_OVERLOAD.hold(element)

    def shape(raw_type: str, element: ...) -> dict[str, Any]: ...  # noqa

    return shape


def serialize_element(raw_type: str, element: Element) -> dict[str, Any]:
    for selection in impl_serialize.select():
        if not selection.harvest(_RAW_TYPE_OVERLOAD, raw_type) or not selection.harvest(
            _ELEMENT_OVERLOAD, element
        ):
            continue

        selection.complete()

    return selection(raw_type, element)  # type: ignore  # noqa


# <editor-fold desc="Serialize (json)">
# <editor-fold desc="Standard Core Elements">
@global_collect
@impl_serialize(raw_type="json", element=CoreText)
def serialize_json_text(raw_type: str, element: CoreText) -> dict:
    return {"_type": "Text", "text": element.text, "style": element.style}


@global_collect
@impl_serialize(raw_type="json", element=CoreNotice)
def serialize_json_notice(raw_type: str, element: CoreNotice) -> dict:
    return {
        "_type": "Notice",
        "target": element.target.display,
        "display": element.display,
    }


@global_collect
@impl_serialize(raw_type="json", element=CoreNoticeAll)
def serialize_json_notice_all(raw_type: str, element: CoreNoticeAll) -> dict:
    return {"_type": "NoticeAll"}


@global_collect
@impl_serialize(raw_type="json", element=CorePicture)
def serialize_json_picture(raw_type: str, element: CorePicture) -> dict:
    return {"_type": "Picture", "resource": element.resource.to_selector().display}


@global_collect
@impl_serialize(raw_type="json", element=CoreAudio)
def serialize_json_audio(raw_type: str, element: CoreAudio) -> dict:
    return {
        "_type": "Audio",
        "resource": element.resource.to_selector().display,
        "duration": element.duration,
    }


@global_collect
@impl_serialize(raw_type="json", element=CoreVideo)
def serialize_json_video(raw_type: str, element: CoreVideo) -> dict:
    return {"_type": "Video", "resource": element.resource.to_selector().display}


@global_collect
@impl_serialize(raw_type="json", element=CoreFile)
def serialize_json_file(raw_type: str, element: CoreFile) -> dict:
    return {"_type": "File", "resource": element.resource.to_selector().display}


@global_collect
@impl_serialize(raw_type="json", element=CoreReference)
def serialize_json_reference(raw_type: str, element: CoreReference) -> dict:
    return {
        "_type": "Reference",
        "resource": element.message.to_selector().display,
        "slice": list(element.slice or []),
    }


@global_collect
@impl_serialize(raw_type="json", element=CoreFace)
def serialize_json_face(raw_type: str, element: CoreFace) -> dict:
    return {"_type": "Face", "id": element.id, "name": element.name}


# </editor-fold>
# <editor-fold desc="Standard QQ Elements">
@global_collect
@impl_serialize(raw_type="json", element=QqMarketFace)
def serialize_json_qq_market_face(raw_type: str, element: QqMarketFace) -> dict:
    return {
        "_type": "QQ::MarketFace",
        "resource": (
            element.resource.to_selector().display  # type: ignore
            if hasattr(element, "resource")
            else None
        ),
        "id": element.id,
        "tab_id": element.tab_id,
        "key": element.key,
        "summary": element.summary,
    }


@global_collect
@impl_serialize(raw_type="json", element=QqJson)
def serialize_json_qq_json(raw_type: str, element: QqJson) -> dict:
    return {"_type": "QQ::Json", "content": element.content}


@global_collect
@impl_serialize(raw_type="json", element=QqXml)
def serialize_json_qq_xml(raw_type: str, element: QqXml) -> dict:
    return {"_type": "QQ::Xml", "content": element.content}


@global_collect
@impl_serialize(raw_type="json", element=QqPoke)
def serialize_json_qq_poke(raw_type: str, element: QqPoke) -> dict:
    return {"_type": "QQ::Poke", "kind": str(element.kind)}


@global_collect
@impl_serialize(raw_type="json", element=QqApp)
def serialize_json_qq_app(raw_type: str, element: QqApp) -> dict:
    return {"_type": "QQ::App", "content": element.content}


@global_collect
@impl_serialize(raw_type="json", element=QqDice)
def serialize_json_qq_dice(raw_type: str, element: QqDice) -> dict:
    return {"_type": "QQ::Dice", "value": element.value}


@global_collect
@impl_serialize(raw_type="json", element=QqFlashImage)
def serialize_json_qq_flash_image(raw_type: str, element: QqFlashImage) -> dict:
    return {
        "_type": "QQ::FlashImage",
        "resource": element.resource.to_selector().display,
    }


@global_collect
@impl_serialize(raw_type="json", element=QqForward)
def serialize_json_qq_forward(raw_type: str, element: QqForward) -> dict:
    return {
        "_type": "QQ::Forward",
        "id": element.id.to_selector().display if element.id else None,
    }


@global_collect
@impl_serialize(raw_type="json", element=QqMusicShare)
def serialize_json_qq_music_share(raw_type: str, element: QqMusicShare) -> dict:
    return {
        "_type": "QQ::MusicShare",
        "kind": str(element.kind),
        "title": element.title,
        "content": element.content,
        "url": element.url,
        "thumbnail": element.thumbnail,
        "audio": element.audio,
        "brief": element.brief,
    }


@global_collect
@impl_serialize(raw_type="json", element=QqShare)
def serialize_json_qq_share(raw_type: str, element: QqShare) -> dict:
    return {
        "_type": "QQ::Share",
        "url": element.url,
        "title": element.title,
        "content": element.content,
        "thumbnail": element.thumbnail,
    }


@global_collect
@impl_serialize(raw_type="json", element=QqGift)
def serialize_json_qq_gift(raw_type: str, element: QqGift) -> dict:
    return {
        "_type": "QQ::Gift",
        "kind": str(element.kind),
        "target": element.target.to_selector().display,
    }


# </editor-fold>
# <editor-fold desc="Standard Telegram Elements">
@global_collect
@impl_serialize(raw_type="json", element=TgPicture)
def serialize_json_tg_picture(raw_type: str, element: TgPicture) -> dict:
    return {
        "_type": "TG::Picture",
        "resource": element.resource.to_selector().display,
        "has_spoiler": element.has_spoiler,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgVideo)
def serialize_json_tg_video(raw_type: str, element: TgVideo) -> dict:
    return {
        "_type": "TG::Video",
        "resource": element.resource.to_selector().display,
        "has_spoiler": element.has_spoiler,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgAnimation)
def serialize_json_tg_animation(raw_type: str, element: TgAnimation) -> dict:
    return {
        "_type": "TG::Animation",
        "resource": element.resource.to_selector().display,
        "width": element.width,
        "height": element.height,
        "duration": element.duration,
        "has_spoiler": element.has_spoiler,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgContact)
def serialize_json_tg_contact(raw_type: str, element: TgContact) -> dict:
    return {
        "_type": "TG::Contact",
        "phone_number": element.phone_number,
        "first_name": element.first_name,
        "last_name": element.last_name,
        "vcard": element.vcard,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgLocation)
def serialize_json_tg_location(raw_type: str, element: TgLocation) -> dict:
    return {
        "_type": "TG::Location",
        "latitude": element.latitude,
        "longitude": element.longitude,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgSticker)
def serialize_json_tg_sticker(raw_type: str, element: TgSticker) -> dict:
    return {
        "_type": "TG::Sticker",
        "resource": element.resource.to_selector().display,
        "width": element.width,
        "height": element.height,
        "is_animated": element.is_animated,
        "is_video": element.is_video,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgVenue)
def serialize_json_tg_venue(raw_type: str, element: TgVenue) -> dict:
    return {
        "_type": "TG::Venue",
        "latitude": element.latitude,
        "longitude": element.longitude,
        "title": element.title,
        "address": element.address,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgVideoNote)
def serialize_json_tg_video_note(raw_type: str, element: TgVideoNote) -> dict:
    return {
        "_type": "TG::VideoNote",
        "resource": element.resource.to_selector().display,
    }


@global_collect
@impl_serialize(raw_type="json", element=TgDice)
def serialize_json_tg_dice(raw_type: str, element: TgDice) -> dict:
    return {"_type": "TG::Dice", "value": element.value, "emoji": str(element.emoji)}


@global_collect
@impl_serialize(raw_type="json", element=TgStory)
def serialize_json_tg_story(raw_type: str, element: TgStory) -> dict:
    return {"_type": "TG::Story"}


# </editor-fold>
# </editor-fold>


def serialize(chain: MessageChain) -> str:
    return "json:" + json.dumps(
        [serialize_element("json", element) for element in chain], ensure_ascii=False
    )
