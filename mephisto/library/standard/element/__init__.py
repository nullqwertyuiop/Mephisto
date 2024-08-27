from mephisto.library.model.metadata import StandardMetadata
from .qq import MarketFace

__all__ = ["MarketFace"]


def export() -> StandardMetadata:
    return StandardMetadata(
        identifier="library.standard.element",
        name="Elements",
        version="0.0.1",
        description="A standard for elements",
        author=["nullqwertyuiop"],
    )
