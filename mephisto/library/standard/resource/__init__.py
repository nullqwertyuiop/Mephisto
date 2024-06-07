from mephisto.library.model.metadata import StandardMetadata


def export() -> StandardMetadata:
    return StandardMetadata(
        identifier="library.standard.resource",
        name="Resources",
        version="0.0.1",
        description="A standard for resources",
        author=["nullqwertyuiop"],
    )
