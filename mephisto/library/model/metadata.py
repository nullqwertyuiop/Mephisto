from functools import partial
from pathlib import Path
from typing import Annotated, Literal

from packaging.version import Version
from pydantic import AfterValidator, BaseModel, Field

from mephisto.library.util.context import module_instance
from mephisto.shared import MEPHISTO_ROOT


def _version_validator(v: str):
    Version(v)
    return v


def _identifier_validator(scope: str, v: str):
    if not v.startswith(f"{scope}.") and not v.startswith(f"library.{scope}."):
        raise ValueError(f'{scope.capitalize()} identifier must start with "{scope}."')
    if not v.lstrip("library.").lstrip(f"{scope}."):
        raise ValueError(f"{scope.capitalize()} identifier cannot be empty")
    if v[0].isdigit():
        raise ValueError(f"{scope.capitalize()} identifier cannot start with a digit")
    if [
        char
        for char in v.lstrip("library.").lstrip(f"{scope}.")
        if not char.isalnum() and char not in ["_", "."]
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
    authors: list[dict[str, str]] = Field(default_factory=list)

    def __hash__(self):
        return hash(self.__class__.__name__ + self.identifier)

    @property
    def stem(self):
        return self.identifier.lstrip("library.").lstrip(f"{self.type}.")

    @property
    def path(self):
        return Path(MEPHISTO_ROOT, *self.identifier.split("."))


class StandardMetadata(MephistoMetadata):
    type: Literal["standard"] = "standard"
    identifier: Annotated[str, AfterValidator(_standard_identifier_validator)]


class ModuleMetadata(MephistoMetadata):
    type: Literal["module"] = "module"
    identifier: Annotated[str, AfterValidator(_module_identifier_validator)]
    dependencies: list["ModuleMetadata"] = Field(default_factory=list)
    standards: list[StandardMetadata] = Field(default_factory=list)

    @property
    def entrypoint(self):
        return f"{self.identifier}.main"

    @property
    def readme(self) -> Path:
        return self.path / "README.md"

    @property
    def assets(self) -> Path:
        return self.path / "assets"

    @staticmethod
    def current() -> "ModuleMetadata":
        return module_instance.get()
