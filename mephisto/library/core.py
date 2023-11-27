import os
import pkgutil
from pathlib import Path

from avilla.core import Avilla
from creart import it
from graia.saya import Saya
from launart import Launart, Service
from loguru import logger


class MephistoServiceEssential(Service):
    id = "mephisto.service/essential"
    avilla: Avilla

    def __init__(self):
        self.avilla = Avilla()
        self._init_test_protocols()
        self._require_modules(Path("library") / "module")
        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @staticmethod
    def _require_modules(*paths: Path):
        saya = it(Saya)
        with saya.module_context():
            for path in paths:
                for module in pkgutil.iter_modules([str(path)]):
                    saya.require((path / module.name).as_posix().replace("/", "."))

    def _init_test_protocols(self):
        # IMPORTANT: Test-only

        from avilla.telegram.protocol import TelegramBotConfig, TelegramProtocol

        config = TelegramBotConfig(os.environ["TELEGRAM_TOKEN"], reformat=True)
        self.avilla.apply_protocols(TelegramProtocol().configure(config))

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            logger.success("[MephistoService] Current stage: preparing")

        async with self.stage("cleanup"):
            logger.success("[MephistoService] Current stage: cleanup")


def launch():
    mgr = it(Launart)
    mgr.add_component(MephistoServiceEssential())
    mgr.launch_blocking()
