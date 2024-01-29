import pkgutil
from pathlib import Path

from avilla.core import Avilla
from creart import it
from graia.saya import Saya
from launart import Launart, Service
from loguru import logger


class MephistoService(Service):
    id = "mephisto.service/essential"
    _avilla: Avilla

    @property
    def avilla(self):
        return self._avilla

    @property
    def required(self):
        return {
            "mephisto.service/session",
            "mephisto.service/config",
            "mephisto.service/protocol",
        }

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @staticmethod
    def require_modules(*paths: Path):
        saya = it(Saya)
        with saya.module_context():
            for path in paths:
                for module in pkgutil.iter_modules([str(path)]):
                    saya.require((path / module.name).as_posix().replace("/", "."))

    async def launch(self, manager: Launart):
        self._avilla = Avilla()
        self.require_modules(Path("library") / "module")

        async with self.stage("preparing"):
            logger.success("[MephistoService] Current stage: preparing")

        async with self.stage("cleanup"):
            logger.success("[MephistoService] Current stage: cleanup")
