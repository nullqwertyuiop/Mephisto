from graia.amnesia.message import Element
from graia.ryanvk import Capability, Fn, TypeOverload

from mephisto.library.model.metadata import StandardMetadata


class ModerationCapability(Capability):
    @Fn.complex({TypeOverload(): ["element"]})
    async def check(self, element: Element) -> bool:
        ...


def export() -> StandardMetadata:
    return StandardMetadata(
        identifier="library.standard.moderation",
        name="Moderation",
        version="0.0.1",
        description="A standard for moderation",
        author=["nullqwertyuiop"],
    )
