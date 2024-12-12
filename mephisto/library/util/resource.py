from typing import Callable, cast

from avilla.core import Context, Notice, Picture, RawResource, Resource, Text, Video
from avilla.standard.core.profile import Nick
from avilla.standard.telegram.elements import Animation as TelegramAnimation
from avilla.standard.telegram.elements import Picture as TelegramPicture
from avilla.standard.telegram.elements import Sticker as TelegramSticker
from avilla.standard.telegram.elements import Video as TelegramVideo
from avilla.telegram.resource import TelegramAnimationResource, TelegramStickerResource
from graia.amnesia.message import Element, MessageChain


class ResourcedElement(Element):
    resource: Resource


def parse_telegram_animation(element: ResourcedElement) -> Element:
    if isinstance(element.resource, TelegramAnimationResource):
        if element.resource.mime_type == "video/mp4":
            return Video(element.resource)
        return Picture(element.resource)
    return Picture(element.resource)


def parse_telegram_sticker(element: ResourcedElement) -> Element:
    if isinstance(element.resource, TelegramStickerResource):
        if element.resource.is_video:
            return Video(element.resource)
        return Picture(element.resource)
    return Picture(element.resource)


PARSER_MAP: dict[type, Callable[[ResourcedElement], Element]] = {
    TelegramPicture: lambda _: Picture(_.resource),
    TelegramVideo: lambda _: Video(_.resource),
    TelegramAnimation: parse_telegram_animation,
    TelegramSticker: parse_telegram_sticker,
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
        if type(element) not in PARSER_MAP:
            elements.append(element)
            continue
        element = cast(ResourcedElement, element)
        elements.append(PARSER_MAP[type(element)](element))
    return MessageChain(elements)
