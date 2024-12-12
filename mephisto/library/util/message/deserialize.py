import json
import re
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
from avilla.core.selector import Selector
from avilla.standard.qq.elements import App as QqApp
from avilla.standard.qq.elements import Dice as QqDice
from avilla.standard.qq.elements import FlashImage as QqFlashImage
from avilla.standard.qq.elements import Forward as QqForward
from avilla.standard.qq.elements import Gift as QqGift
from avilla.standard.qq.elements import GiftKind as QqGiftKind
from avilla.standard.qq.elements import Json as QqJson
from avilla.standard.qq.elements import MarketFace as QqMarketFace
from avilla.standard.qq.elements import MusicShare as QqMusicShare
from avilla.standard.qq.elements import MusicShareKind as QqMusicShareKind
from avilla.standard.qq.elements import Poke as QqPoke
from avilla.standard.qq.elements import PokeKind as QqPokeKind
from avilla.standard.qq.elements import Share as QqShare
from avilla.standard.qq.elements import Xml as QqXml
from avilla.standard.telegram.elements import Animation as TgAnimation
from avilla.standard.telegram.elements import Contact as TgContact
from avilla.standard.telegram.elements import Dice as TgDice
from avilla.standard.telegram.elements import DiceEmoji as TgDiceEmoji
from avilla.standard.telegram.elements import Location as TgLocation
from avilla.standard.telegram.elements import Picture as TgPicture
from avilla.standard.telegram.elements import Sticker as TgSticker
from avilla.standard.telegram.elements import Story as TgStory
from avilla.standard.telegram.elements import Venue as TgVenue
from avilla.standard.telegram.elements import Video as TgVideo
from avilla.standard.telegram.elements import VideoNote as TgVideoNote
from flywheel import FnCollectEndpoint, SimpleOverload, global_collect
from graia.amnesia.message.chain import MessageChain
from graia.amnesia.message.element import Element

from mephisto.library.model.exception import MessageDeserializationFailed
from mephisto.library.util.message.resource import RecordAttachmentResource

_ELEMENT_OVERLOAD = SimpleOverload("element")
_RAW_TYPE_OVERLOAD = SimpleOverload("raw_type")


@FnCollectEndpoint
def impl_deserialize(raw_type: str, element: str):
    yield _ELEMENT_OVERLOAD.hold(element)
    yield _RAW_TYPE_OVERLOAD.hold(raw_type)

    def shape(raw_type: str, element: str, raw: Any) -> Element: ...  # noqa

    return shape


def deserialize_element(raw_type: str, element: str, raw: Any) -> Element:
    for selection in impl_deserialize.select():
        if not selection.harvest(_ELEMENT_OVERLOAD, element) or not selection.harvest(
            _RAW_TYPE_OVERLOAD, raw_type
        ):
            continue

        selection.complete()

    return selection(raw_type, element, raw)  # type: ignore  # noqa


# <editor-fold desc="Deserialize">
# <editor-fold desc="Deserialize (repr)">
# Reserved for backward compatibility
@global_collect
@impl_deserialize(raw_type="repr", element="Text")
def deserialize_repr_text(raw_type: str, element: str, raw: str) -> CoreText:
    pattern = r"(?P<element>Text)\(text=(?P<text>.+?)(?:, style=(?P<style>.+?))?\)"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CoreText(match["text"], match["style"])


@global_collect
@impl_deserialize(raw_type="repr", element="Notice")
def deserialize_repr_notice(raw_type: str, element: str, raw: str) -> CoreNotice:
    pattern = r"\[\$?(?P<element>Notice):target=(?P<target>.+?)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CoreNotice(
        Selector.from_follows(match["target"].split("Selector().")[-1]),
    )


@global_collect
@impl_deserialize(raw_type="repr", element="NoticeAll")
def deserialize_repr_notice_all(raw_type: str, element: str, raw: str) -> CoreNoticeAll:
    return CoreNoticeAll()


@global_collect
@impl_deserialize(raw_type="repr", element="Picture")
def deserialize_repr_picture(raw_type: str, element: str, raw: str) -> CorePicture:
    pattern = r"\[\$?(?P<element>Picture):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CorePicture(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Audio")
def deserialize_repr_audio(raw_type: str, element: str, raw: str) -> CoreAudio:
    pattern = r"\[\$?(?P<element>Audio):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CoreAudio(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Video")
def deserialize_repr_video(raw_type: str, element: str, raw: str) -> CoreVideo:
    pattern = r"\[\$?(?P<element>Video):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CoreVideo(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="File")
def deserialize_repr_file(raw_type: str, element: str, raw: str) -> CoreFile:
    pattern = r"\[\$?(?P<element>File):resource=(?P<resource>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CoreFile(
        RecordAttachmentResource(
            Selector.from_follows(match["resource"].split("Selector().")[-1])
        )
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Reference")
def deserialize_repr_reference(raw_type: str, element: str, raw: str) -> CoreReference:
    pattern = r"\[\$?(?P<element>Reference):id=(?P<message>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CoreReference(
        Selector.from_follows(match["message"]),
    )


@global_collect
@impl_deserialize(raw_type="repr", element="Face")
def deserialize_repr_face(raw_type: str, element: str, raw: str) -> CoreFace:
    pattern = r"\[\$?(?P<element>Face):id=(?P<id>.+);name=(?P<name>.+)]"
    if not (match := re.match(pattern, raw)):
        raise MessageDeserializationFailed(element=element, raw_type=raw_type, raw=raw)
    return CoreFace(
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
# <editor-fold desc="Standard Core Elements">
@global_collect
@impl_deserialize(raw_type="json", element="Text")
def deserialize_json_text(raw_type: str, element: str, raw: dict[str, Any]) -> CoreText:
    return CoreText(raw["text"], style=raw.get("style"))


@global_collect
@impl_deserialize(raw_type="json", element="Notice")
def deserialize_json_notice(
    raw_type: str, element: str, raw: dict[str, Any]
) -> CoreNotice:
    return CoreNotice(Selector.from_follows(raw["target"]), display=raw.get("display"))


@global_collect
@impl_deserialize(raw_type="json", element="NoticeAll")
def deserialize_json_notice_all(
    raw_type: str, element: str, raw: dict[str, Any]
) -> CoreNoticeAll:
    return CoreNoticeAll()


@global_collect
@impl_deserialize(raw_type="json", element="Picture")
def deserialize_json_picture(
    raw_type: str, element: str, raw: dict[str, Any]
) -> CorePicture:
    return CorePicture(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
    )


@global_collect
@impl_deserialize(raw_type="json", element="Audio")
def deserialize_json_audio(
    raw_type: str, element: str, raw: dict[str, Any]
) -> CoreAudio:
    return CoreAudio(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
        duration=(
            int(duration) if (duration := raw.get("duration", "")).isdigit() else -1
        ),
    )


@global_collect
@impl_deserialize(raw_type="json", element="Video")
def deserialize_json_video(
    raw_type: str, element: str, raw: dict[str, Any]
) -> CoreVideo:
    return CoreVideo(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
    )


@global_collect
@impl_deserialize(raw_type="json", element="File")
def deserialize_json_file(raw_type: str, element: str, raw: dict[str, Any]) -> CoreFile:
    return CoreFile(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
    )


@global_collect
@impl_deserialize(raw_type="json", element="Reference")
def deserialize_json_reference(
    raw_type: str, element: str, raw: dict[str, Any]
) -> CoreReference:
    if ref_slice := raw.get("slice"):
        if (
            len(ref_slice) == 2
            and isinstance(ref_slice[0], int)
            and isinstance(ref_slice[1], int)
        ):
            return CoreReference(
                Selector.from_follows(raw["resource"]),
                slice=(ref_slice[0], ref_slice[1]),
            )
    return CoreReference(Selector.from_follows(raw["resource"]), slice=None)


@global_collect
@impl_deserialize(raw_type="json", element="Face")
def deserialize_json_face(raw_type: str, element: str, raw: dict[str, Any]) -> CoreFace:
    return CoreFace(raw["id"], name=raw.get("name"))


# </editor-fold>
# <editor-fold desc="Standard QQ Elements">
@global_collect
@impl_deserialize(
    raw_type="json", element="MarketFace"
)  # reserved for backward compatibility
@impl_deserialize(raw_type="json", element="QQ::MarketFace")
def deserialize_json_market_face(
    raw_type: str, element: str, raw: dict[str, Any]
) -> CorePicture | QqMarketFace:
    if raw["resource"]:
        return CorePicture(
            RecordAttachmentResource(Selector.from_follows(raw["resource"]))
        )
    else:
        return QqMarketFace(
            id=raw["id"],
            key=raw.get("key"),
            tab_id=raw.get("tab_id"),
            summary=raw.get("summary"),
        )


@global_collect
@impl_deserialize(raw_type="json", element="QQ::Json")
def deserialize_json_json(raw_type: str, element: str, raw: dict[str, Any]) -> QqJson:
    return QqJson(content=raw["content"])


@global_collect
@impl_deserialize(raw_type="json", element="QQ::Xml")
def deserialize_json_xml(raw_type: str, element: str, raw: dict[str, Any]) -> QqXml:
    return QqXml(content=raw["content"])


@global_collect
@impl_deserialize(raw_type="json", element="QQ::Poke")
def deserialize_json_poke(raw_type: str, element: str, raw: dict[str, Any]) -> QqPoke:
    return QqPoke(kind=QqPokeKind(raw["kind"]))


@global_collect
@impl_deserialize(raw_type="json", element="QQ::App")
def deserialize_json_app(raw_type: str, element: str, raw: dict[str, Any]) -> QqApp:
    return QqApp(content=raw["content"])


@global_collect
@impl_deserialize(raw_type="json", element="QQ::Dice")
def deserialize_json_dice(raw_type: str, element: str, raw: dict[str, Any]) -> QqDice:
    return QqDice(value=raw["value"])


@global_collect
@impl_deserialize(raw_type="json", element="QQ::FlashImage")
def deserialize_json_flash_image(
    raw_type: str, element: str, raw: dict[str, Any]
) -> QqFlashImage:
    return QqFlashImage(
        RecordAttachmentResource(Selector.from_follows(raw["resource"]))
    )


@global_collect
@impl_deserialize(raw_type="json", element="QQ::Forward")
def deserialize_json_forward(
    raw_type: str, element: str, raw: dict[str, Any]
) -> QqForward:
    return QqForward(id=Selector.from_follows(raw["id"]))


@global_collect
@impl_deserialize(raw_type="json", element="QQ::MusicShare")
def deserialize_json_music_share(
    raw_type: str, element: str, raw: dict[str, Any]
) -> QqMusicShare:
    return QqMusicShare(
        kind=QqMusicShareKind(raw["kind"]),
        title=raw["title"],
        content=raw["content"],
        url=raw["url"],
        thumbnail=raw["thumbnail"],
        audio=raw["audio"],
        brief=raw["brief"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="QQ::Share")
def deserialize_json_share(raw_type: str, element: str, raw: dict[str, Any]) -> QqShare:
    return QqShare(
        url=raw["url"],
        title=raw["title"],
        content=raw["content"],
        thumbnail=raw["thumbnail"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="QQ::Gift")
def deserialize_json_gift(raw_type: str, element: str, raw: dict[str, Any]) -> QqGift:
    return QqGift(
        kind=QqGiftKind(raw["kind"]),
        target=Selector.from_follows(raw["target"]),
    )


# </editor-fold>
# <editor-fold desc="Standard Telegram Elements">
@global_collect
@impl_deserialize(raw_type="json", element="TG::Picture")
def deserialize_json_tg_picture(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgPicture:
    return TgPicture(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
        has_spoiler=raw["has_spoiler"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Video")
def deserialize_json_tg_video(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgVideo:
    return TgVideo(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
        has_spoiler=raw["has_spoiler"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Animation")
def deserialize_json_tg_animation(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgAnimation:
    return TgAnimation(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
        width=raw["width"],
        height=raw["height"],
        duration=raw["duration"],
        has_spoiler=raw["has_spoiler"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Contact")
def deserialize_json_tg_contact(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgContact:
    return TgContact(
        phone_number=raw["phone_number"],
        first_name=raw["first_name"],
        last_name=raw["last_name"],
        vcard=raw["vcard"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Location")
def deserialize_json_tg_location(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgLocation:
    return TgLocation(
        longitude=raw["longitude"],
        latitude=raw["latitude"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Sticker")
def deserialize_json_tg_sticker(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgSticker:
    return TgSticker(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
        width=raw["width"],
        height=raw["height"],
        is_animated=raw["is_animated"],
        is_video=raw["is_video"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Venue")
def deserialize_json_tg_venue(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgVenue:
    return TgVenue(
        longitude=raw["longitude"],
        latitude=raw["latitude"],
        title=raw["title"],
        address=raw["address"],
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::VideoNote")
def deserialize_json_tg_video_note(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgVideoNote:
    return TgVideoNote(
        RecordAttachmentResource(Selector.from_follows(raw["resource"])),
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Dice")
def deserialize_json_tg_dice(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgDice:
    return TgDice(
        value=raw["value"],
        emoji=TgDiceEmoji(raw["emoji"]),
    )


@global_collect
@impl_deserialize(raw_type="json", element="TG::Story")
def deserialize_json_tg_story(
    raw_type: str, element: str, raw: dict[str, Any]
) -> TgStory:
    return TgStory()


# </editor-fold>
# </editor-fold>


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
