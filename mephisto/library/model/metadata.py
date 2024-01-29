from typing import Annotated

from packaging.version import Version
from pydantic import AfterValidator, BaseModel


def _version_validator(v: str):
    Version(v)
    return v


class MephistoMetadata(BaseModel):
    identifier: str
    name: str = ""
    version: Annotated[str, AfterValidator(_version_validator)] = "0.1.0"
    description: str = ""


class StandardMetadata(MephistoMetadata):
    dependencies: list["StandardMetadata"] = []


class ModuleMetadata(MephistoMetadata):
    dependencies: list["ModuleMetadata"] = []
    standards: list[StandardMetadata] = []
