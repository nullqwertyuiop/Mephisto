from avilla.core import Resource, Selector


class MarketFaceResource(Resource[bytes]):
    emoji_package_id: int
    emoji_id: str
    key: str
    name: str | None

    def __init__(
        self,
        selector: Selector,
        emoji_package_id: int,
        emoji_id: str,
        key: str,
        name: str | None = None,
    ):
        super().__init__(selector)
        self.emoji_package_id = emoji_package_id
        self.emoji_id = emoji_id
        self.key = key
        self.name = name

    @property
    def url(self):
        return f"https://gxh.vip.qq.com/club/item/parcel/item/{self.emoji_id[:2]}/{self.emoji_id}/raw300.gif"
