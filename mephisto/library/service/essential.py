import os
import pkgutil
from pathlib import Path

from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla
from avilla.telegram.protocol import TelegramBotConfig, TelegramProtocol
from creart import it
from graia.saya import Saya
from launart import Launart, Service
from loguru import logger


class MephistoService(Service):
    id = "mephisto.service/essential"
    _avilla: Avilla

    def __init__(self):
        self._avilla = Avilla()
        self._init_protocols()
        self._require_modules(Path("library") / "module")
        super().__init__()

    @property
    def required(self):
        return {"mephisto.service/session"}

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

    def _init_protocols(self):
        if os.environ.get("MEPHISTO_NO_CONSOLE") != "1":
            self._avilla.apply_protocols(ConsoleProtocol())
        else:
            logger.warning("[MephistoService] Console protocol disabled")

        config = TelegramBotConfig(os.environ["TELEGRAM_TOKEN"], reformat=True)
        self._avilla.apply_protocols(TelegramProtocol().configure(config))

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            logger.success("[MephistoService] Current stage: preparing")

        async with self.stage("cleanup"):
            logger.success("[MephistoService] Current stage: cleanup")
