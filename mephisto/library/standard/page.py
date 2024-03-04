from graia.ryanvk import Capability, Fn, TypeOverload
from pydantic import BaseModel

from mephisto.library.model.metadata import StandardMetadata


class PageElement(BaseModel):
    pass


class Icon(PageElement):
    src: str
    width: int | None = None
    height: int | None = None


class Title(PageElement):
    text: str


class Banner(PageElement):
    text: str
    icon: Icon | None = None


class Button(PageElement):
    text: str
    href: str
    width: int | None = None


class MultimediaBox(PageElement):
    src: str
    alt: str
    width: int | None = None
    height: int | None = None


class ProgressBar(PageElement):
    value: float
    text: str | None = None


class TextItem(PageElement):
    text: str
    description: str | None = None
    icon: Icon | None = None


class TextSwitchItem(PageElement):
    text: str
    description: str | None = None
    icon: Icon | None = None
    active: bool
    href: str = "#"


class GenericBox(PageElement):
    items: list[TextItem | TextSwitchItem]


class Footer(PageElement):
    text: str
    description: str | None = None


class CustomElement(PageElement):
    html: str


class PageBuilder(Capability):
    @Fn.complex({TypeOverload(): ["element"]})
    async def build_element(self, element: PageElement) -> str:
        pass

    @Fn
    async def build_page(self, *elements: PageElement) -> str:
        pass

    @Fn
    async def render(self, *elements: PageElement) -> bytes:
        pass


def export() -> StandardMetadata:
    return StandardMetadata(
        identifier="library.standard.page",
        name="Page",
        version="0.0.1",
        description="A standard for page building",
        author=["nullqwertyuiop"],
    )
