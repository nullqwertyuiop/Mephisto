import pkgutil
from json import JSONDecodeError
from pathlib import Path
from typing import TypeVar

import toml
from creart import it
from graia.saya import Saya
from launart import Launart, Service
from launart.status import Phase
from loguru import logger
from pdm.core import Core as PDMCore
from pdm.models.requirements import FileRequirement
from pydantic import ValidationError

from mephisto.library.model.exception import RequirementResolveFailed
from mephisto.library.model.metadata import ModuleMetadata
from mephisto.shared import MEPHISTO_ROOT

_T = TypeVar("_T")


class ModuleStore:
    modules: set[ModuleMetadata]
    enabled: set[ModuleMetadata]

    def __init__(self, modules: set[ModuleMetadata], enabled: set[ModuleMetadata]):
        self.modules = modules
        self.enabled = enabled

    @property
    def disabled(self):
        return self.modules - self.enabled

    def get(self, identifier: str, _default: _T = None) -> ModuleMetadata | _T:
        return next(
            (module for module in self.modules if module.identifier == identifier),
            _default,
        )


class ModuleService(Service):
    id = "mephisto.service/module"
    modules: set[ModuleMetadata]
    enabled: set[ModuleMetadata]
    supported_interface_types: set = {ModuleStore}

    pdm_core: PDMCore

    def __init__(self):
        self.modules = set()
        self.enabled = set()
        self.pdm_core = PDMCore()
        super().__init__()

    @property
    def required(self):
        return {
            "mephisto.service/data",
            "mephisto.service/standard",
            "mephisto.service/uvicorn",
        }

    @property
    def stages(self) -> set[Phase]:
        return {"preparing", "blocking"}

    def get_interface(self, _: type[ModuleStore]):
        return ModuleStore(self.modules, self.enabled)

    @staticmethod
    def parse_metadata(module: Path) -> ModuleMetadata:
        try:
            pyproject = toml.loads((module / "pyproject.toml").read_text())
            return ModuleMetadata.model_validate(
                pyproject["mephisto"]
                | {
                    "version": pyproject["project"]["version"],
                    "description": pyproject["project"]["description"],
                    "authors": pyproject["project"]["authors"],
                }
            )
        except ValidationError as e:
            logger.error(f"[ModuleService] {module.name} metadata is invalid")
            raise e

    def generate_metadata(self, module: Path) -> ModuleMetadata:
        module = module.resolve().relative_to(MEPHISTO_ROOT)
        name = module.parts[-1]
        identifier = ".".join(module.parts)
        metadata = ModuleMetadata(identifier=identifier, name=name)
        project = self.pdm_core.create_project(module)
        project.pyproject.metadata.update(
            {
                "name": identifier,
                "version": metadata.version,
                "description": metadata.description,
                "dependencies": [],
                "authors": metadata.authors,
            }
        )
        project.pyproject.settings.update({"distribution": True})
        project.pyproject._data.setdefault("build-system", {}).update(  # noqa
            {"requires": ["pdm-backend"], "build-backend": "pdm.backend"}
        )
        project.pyproject._data.setdefault("mephisto", {}).update(  # noqa
            metadata.model_dump(exclude={"type", "version", "description", "authors"})
        )
        project.pyproject.write(show_message=False)
        return metadata

    @staticmethod
    def standardize(module: Path) -> Path:
        if module.is_dir():
            return module
        new_path = module.parent / module.stem
        new_path.mkdir(exist_ok=True)
        (new_path / "__init__.py").touch(exist_ok=True)
        module.rename(new_path / "main.py")
        logger.info(f"[ModuleService] Standardized {module} to {new_path}")
        return new_path

    @staticmethod
    def check_and_cleanup(path: Path):
        # TODO: check if the module is a corpse
        return True

    @staticmethod
    def noload_flag(path: Path):
        return (path / ".noload").exists()

    def prepare_metadata(self, *paths: Path) -> list[ModuleMetadata]:
        prepared: list[ModuleMetadata] = []
        for path in paths:
            if not path.is_dir():
                continue
            for module in pkgutil.iter_modules([str(path)]):
                if not self.check_and_cleanup(path / module.name):
                    logger.warning(
                        f"[ModuleService] Skipped module {module.name} due to empty directory"
                    )
                    continue
                module_path = self.standardize(path / module.name)
                try:
                    metadata = self.parse_metadata(module_path)
                    if self.noload_flag(module_path):
                        logger.warning(
                            f"[ModuleService] Skipped module {module.name} due to noload flag"
                        )
                        continue
                    prepared.append(metadata)
                except (ValidationError, FileNotFoundError, JSONDecodeError):
                    metadata = self.generate_metadata(module_path)
                    if self.noload_flag(module_path):
                        logger.warning(
                            f"[ModuleService] Skipped module {module.name} due to noload flag"
                        )
                        continue
                    prepared.append(metadata)
        return prepared

    @staticmethod
    def resolve(*modules: ModuleMetadata) -> list[ModuleMetadata]:
        resolved: set[str] = set()
        unresolved: set[ModuleMetadata] = set(modules)
        result: list[ModuleMetadata] = []

        logger.info("[ModuleService] Resolving module dependencies")
        layer_count = 0
        while unresolved:
            layer = {
                module
                for module in unresolved
                if {dep.identifier for dep in module.dependencies} <= resolved  # type: ignore
            }
            if not layer:
                logger.error(
                    "[ModuleService] Failed to resolve module dependencies, "
                    "the following modules are unresolved:\n"
                    + ", ".join(module.identifier for module in unresolved)
                )
                raise RequirementResolveFailed(unresolved)
            layer_count += 1
            logger.info(
                f"[ModuleService] Resolved {len(layer)} modules in layer {layer_count}"
            )
            unresolved -= layer
            resolved |= {module.identifier for module in layer}
            result.extend(sorted(layer, key=lambda m: m.identifier))

        logger.success("[ModuleService] Resolved module dependencies")
        return result

    def handle_dependency(self, module: ModuleMetadata):
        project = self.pdm_core.create_project(MEPHISTO_ROOT)
        project.add_dependencies(
            [FileRequirement(name=module.identifier, path=module.path)],
            to_group="mephisto",
            show_message=False,
        )

    def require_modules(self, *modules: ModuleMetadata, retry: bool = True):
        retry_modules = []
        pdm_install = False
        saya = it(Saya)
        with saya.module_context():
            for module in modules:
                try:
                    saya.require(module.entrypoint)
                except ImportError:
                    self.handle_dependency(module)
                    pdm_install = True
                    if retry:
                        retry_modules.append(module)
                except Exception as e:
                    logger.error(
                        f"[ModuleService] Failed to require {module.identifier}: {e}"
                    )
                    if retry:
                        retry_modules.append(module)
        if pdm_install:
            self.pdm_core.main(["lock", "--group", ":all"])
            self.pdm_core.main(["install", "--group", ":all"])
        if retry_modules:
            self.require_modules(*retry_modules, retry=False)
        self.modules |= set(modules)

    def require_path(self, *paths: Path, retry: bool = True):
        prepared = self.prepare_metadata(*paths)
        resolved = self.resolve(*prepared)
        self.require_modules(*resolved, retry=retry)

    async def launch(self, manager: Launart):
        self.require_path(Path("library") / "module", Path("module"))

        async with self.stage("preparing"):
            logger.success("[ModuleService] Required all modules")

        async with self.stage("blocking"):
            await manager.status.wait_for_sigexit()
