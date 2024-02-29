import importlib
import pkgutil
from pathlib import Path
from typing import cast

from graia.ryanvk import BaseCollector, Staff, merge, ref
from launart import Launart, Service
from loguru import logger

from mephisto.library.model.metadata import StandardMetadata


class StandardService(Service):
    id = "mephisto.service/standard"
    standards: set[StandardMetadata]
    artifacts: dict

    def __init__(self):
        self.standards = set()
        self.artifacts = {}
        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing"}

    @property
    def staff(self):
        return Staff([self.artifacts], {})

    def register(self, *args):
        artifacts: list[dict] = []
        for perform in args:
            collector: BaseCollector = perform.__collector__
            namespace = collector.namespace or "unknown"
            identify = collector.identify or "unknown"
            artifacts.append(ref(namespace, identify))
            logger.success(
                f"[StandardService] Registered {namespace}::{identify} from {perform.__name__}"
            )
        self.artifacts = {**merge(self.artifacts, *artifacts)}

    @staticmethod
    def check_and_cleanup(path: Path):
        if path.is_file():
            return True
        if not any(path.iterdir()):
            path.rmdir()
            return False

    def require_standards(self, *paths: Path):
        for path in paths:
            if not path.is_dir():
                continue
            for module in pkgutil.iter_modules([str(path)]):
                module_name = (path / module.name).as_posix().replace("/", ".")
                standard = importlib.import_module(module_name, module_name).export()
                standard = cast(StandardMetadata, standard)
                self.standards.add(standard)
                logger.success(
                    f"[StandardService] Loaded standard {standard.identifier}"
                )

    async def launch(self, manager: Launart):
        self.require_standards(Path("library") / "standard", Path("standard"))

        async with self.stage("preparing"):
            logger.success("[StandardService] Required all standard")
