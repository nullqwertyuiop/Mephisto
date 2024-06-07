from avilla.core import Picture

from mephisto.library.standard.resource.qq import MarketFaceResource


class MarketFace(Picture):
    resource: MarketFaceResource  # type: ignore

    def __init__(self, resource: MarketFaceResource):
        super().__init__(resource)

    def __str__(self) -> str:
        return "[$MarketFace]"

    def __repr__(self):
        return f"[$MarketFace:resource={self.resource.to_selector()}]"

    def __eq__(self, other):
        return (
            isinstance(other, MarketFace)
            and self.resource.to_selector() == other.resource.to_selector()
        )
