from pathlib import Path

from avilla.core import Avilla
from launart import Launart, Service
from loguru import logger

from mephisto.shared import MEPHISTO_ROOT


class MephistoService(Service):
    id = "mephisto.service/essential"
    _avilla: Avilla

    @property
    def avilla(self):
        return self._avilla

    @property
    def required(self):
        return {
            "mephisto.service/config",
            "mephisto.service/module",
            "mephisto.service/protocol",
            "mephisto.service/session",
        }

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @staticmethod
    def ensure_path(path: str):
        if not (p := Path(MEPHISTO_ROOT, path)).is_dir():
            p.mkdir(parents=True)

    async def launch(self, manager: Launart):
        self._avilla = Avilla()

        self.ensure_path("config")
        self.ensure_path("data")
        self.ensure_path("module")
        self.ensure_path("standard")
        logger.success("[MephistoService] Ensured all paths")

        async with self.stage("preparing"):
            logger.info("[MephistoService] Current stage: preparing")

        async with self.stage("cleanup"):
            logger.info("[MephistoService] Current stage: cleanup")
