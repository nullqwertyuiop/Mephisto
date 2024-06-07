from typing import Callable, cast

from avilla.core import Context, RawResource, Resource, Picture, Video, Notice
from avilla.standard.core.profile import Nick
from avilla.standard.telegram.elements import (
    Picture as TelegramPicture,
    Video as TelegramVideo,
    Animation,
    Sticker,
)
from avilla.telegram.resource import TelegramStickerResource, TelegramAnimationResource
from graia.amnesia.message import Element, MessageChain, Text

from mephisto.library.standard.element.qq import MarketFace


class __ResourcedElement(Element):
    resource: Resource


def __animation(element: __ResourcedElement) -> Element:
    if isinstance(element.resource, TelegramAnimationResource):
        if element.resource.mime_type == "video/mp4":
            return Video(element.resource)
        return Picture(element.resource)
    return Picture(element.resource)


def __sticker(element: __ResourcedElement) -> Element:
    if isinstance(element.resource, TelegramStickerResource):
        if element.resource.is_video:
            return Video(element.resource)
        return Picture(element.resource)
    return Picture(element.resource)


COMPATIBLE_MAP: dict[type, Callable[[__ResourcedElement], Element]] = {
    TelegramPicture: lambda _: Picture(_.resource),
    TelegramVideo: lambda _: Video(_.resource),
    Animation: __animation,
    Sticker: __sticker,
    MarketFace: lambda _: Picture(_.resource),
}


async def fetch_all(ctx: Context, message: MessageChain):
    elements: list[Element] = []
    for element in message:
        if getattr(element, "resource", None) is None or not isinstance(
            getattr(element, "resource"), Resource
        ):
            elements.append(element)
            continue
        data: bytes = await ctx.fetch(getattr(element, "resource"))
        elements.append(type(element)(RawResource(data)))  # type: ignore
    return MessageChain(elements)


async def generalize_all(
    ctx: Context, message: MessageChain, fetch: bool = True, pull: bool = True
):
    if fetch:
        message = await fetch_all(ctx, message)
    elements: list[Element] = []
    for element in message:
        if isinstance(element, Notice):
            if pull:
                nick = await ctx.pull(Nick, element.target)
                elements.append(Text(f"@{nick.name}"))
            else:
                elements.append(
                    Text(element.display or f"@{element.target.last_value}")
                )
            continue
        if getattr(element, "resource", None) is None or not isinstance(
            getattr(element, "resource"), Resource
        ):
            elements.append(element)
            continue
        if type(element) not in COMPATIBLE_MAP:
            elements.append(element)
            continue
        element = cast(__ResourcedElement, element)
        elements.append(COMPATIBLE_MAP[type(element)](element))
    return MessageChain(elements)
