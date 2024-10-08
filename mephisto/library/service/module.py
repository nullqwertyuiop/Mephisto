import json
import pkgutil
from json import JSONDecodeError
from pathlib import Path
from typing import TypeVar

from creart import it
from graia.saya import Saya
from launart import Launart, Service
from launart.status import Phase
from loguru import logger
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

    def __init__(self):
        self.modules = set()
        self.enabled = set()
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
            return ModuleMetadata.model_validate_json(
                (module / "metadata.json").read_text()
            )
        except ValidationError as e:
            logger.error(f"[ModuleService] {module.name} metadata is invalid")
            raise e

    @staticmethod
    def generate_metadata(module: Path) -> ModuleMetadata:
        module = module.resolve().relative_to(MEPHISTO_ROOT)
        name = module.parts[-1]
        identifier = ".".join(module.parts)
        return ModuleMetadata(identifier=identifier, name=name)

    @staticmethod
    def write_metadata(metadata: ModuleMetadata):
        module_path = Path(metadata.identifier.replace(".", "/"))
        with (module_path / "metadata.json").open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    metadata.model_dump(exclude={"type"}), indent=4, ensure_ascii=False
                )
            )
            f.write("\n")

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
                    self.write_metadata(metadata)
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
                if {dep.identifier for dep in module.dependencies} <= resolved
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

    def require_modules(self, *paths: Path):
        saya = it(Saya)
        prepared = self.prepare_metadata(*paths)
        resolved = self.resolve(*prepared)
        with saya.module_context():
            for module in resolved:
                saya.require(module.entrypoint)
        self.modules |= set(resolved)

    async def launch(self, manager: Launart):
        self.require_modules(Path("library") / "module", Path("module"))

        async with self.stage("preparing"):
            logger.success("[ModuleService] Required all modules")

        async with self.stage("blocking"):
            await manager.status.wait_for_sigexit()
