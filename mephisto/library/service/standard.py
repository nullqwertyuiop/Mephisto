import importlib
import pkgutil
from pathlib import Path
from typing import cast

from launart import Launart, Service
from loguru import logger

from mephisto.library.model.metadata import StandardMetadata


class StandardService(Service):
    id = "mephisto.service/standard"
    standards: set[StandardMetadata]

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing"}

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
                if not self.check_and_cleanup(path / module.name):
                    logger.warning(
                        f"[StandardService] Skipped standard {module.name} due to empty directory"
                    )
                    continue
                module_name = (path / module.name).as_posix().replace("/", ".")
                standard = importlib.import_module(module_name, module_name).export()
                standard = cast(StandardMetadata, standard)
                self.standards.add(standard)
                logger.success(
                    f"[StandardService] Loaded standard {standard.identifier}"
                )

    async def launch(self, manager: Launart):
        self.standards = set()
        self.require_standards(Path("library") / "standard", Path("standard"))

        async with self.stage("preparing"):
            logger.success("[StandardService] Required all standards")
