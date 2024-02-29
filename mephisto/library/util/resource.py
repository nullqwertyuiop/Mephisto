from avilla.core import Context, Picture, RawResource, Resource
from graia.amnesia.message import Element, MessageChain


async def fetch_all(ctx: Context, message: MessageChain):
    elements: list[Element] = []
    for element in message:
        if getattr(element, "resource", None) is None or not isinstance(
            getattr(element, "resource"), Resource
        ):
            elements.append(element)
            continue
        data: bytes = await ctx.fetch(getattr(element, "resource"))
        elements.append(Picture(RawResource(data)))
    return MessageChain(elements)
