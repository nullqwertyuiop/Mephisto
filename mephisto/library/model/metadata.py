from functools import partial
from typing import Annotated, Literal

from packaging.version import Version
from pydantic import AfterValidator, BaseModel


def _version_validator(v: str):
    Version(v)
    return v


def _identifier_validator(scope: str, v: str):
    if not v.startswith(f"{scope}.") and not v.startswith(f"library.{scope}."):
        raise ValueError(f'{scope.capitalize()} identifier must start with "{scope}."')
    if not v.lstrip("library.").lstrip(f"{scope}."):
        raise ValueError(f"{scope.capitalize()} identifier cannot be empty")
    if [
        char
        for char in v.lstrip("library.").lstrip(f"{scope}.")
        if (char == "-" or not char.isalnum())
    ]:
        raise ValueError(f"{scope.capitalize()} identifier invalid")
    return v


_standard_identifier_validator = partial(_identifier_validator, "standard")
_module_identifier_validator = partial(_identifier_validator, "module")


class MephistoMetadata(BaseModel):
    type: str
    identifier: str
    name: str = ""
    version: Annotated[str, AfterValidator(_version_validator)] = "0.1.0"
    description: str = ""
    author: list[str] = []

    def __hash__(self):
        return hash(self.__class__.__name__ + self.identifier)


class StandardMetadata(MephistoMetadata):
    type: Literal["standard"] = "standard"
    identifier: Annotated[str, AfterValidator(_standard_identifier_validator)]


class ModuleMetadata(MephistoMetadata):
    type: Literal["module"] = "module"
    identifier: Annotated[str, AfterValidator(_module_identifier_validator)]
    dependencies: list["ModuleMetadata"] = []
    standards: list[StandardMetadata] = []
