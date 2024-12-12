from pathlib import Path

from avilla.core import Avilla
from kayaku import create
from launart import Launart, Service
from launart.status import Phase
from loguru import logger

from mephisto.library.model.config import MephistoConfig
from mephisto.shared import MEPHISTO_REPO, MEPHISTO_ROOT


class MephistoService(Service):
    id = "mephisto.service/essential"
    avilla: Avilla

    @property
    def broadcast(self):
        return self.avilla.broadcast

    def __init__(self):
        self.ensure_path("config")
        self.ensure_path("data")
        self.ensure_path("module")
        self.ensure_path("standard")
        logger.success("[MephistoService] Ensured all paths")

        cfg: MephistoConfig = create(MephistoConfig)

        self.avilla = Avilla(message_cache_size=cfg.advanced.message_cache_size)
        self.apply_perform()
        logger.debug("[MephistoService] Initialized Avilla")

        super().__init__()

    @property
    def required(self):
        return {
            "mephisto.service/data",
            "mephisto.service/module",
            "mephisto.service/protocol",
            "mephisto.service/session",
            "mephisto.service/uvicorn",
        }

    @property
    def stages(self) -> set[Phase]:
        return {"preparing", "cleanup"}

    @staticmethod
    def ensure_path(path: str):
        if not (p := Path(MEPHISTO_ROOT, path)).is_dir():
            p.mkdir(parents=True)

    def apply_perform(self):
        from mephisto.library.util.message.resource import RecordResourceFetchPerform

        RecordResourceFetchPerform.apply_to(self.avilla.global_artifacts)
        logger.debug("[MephistoService] Applied RecordResourceFetchPerform to Avilla")

    async def launch(self, manager: Launart):

        async with self.stage("preparing"):
            logger.info("[MephistoService] Current stage: preparing")

            # TODO: Move into Updater
            logger.info(
                f"[MephistoService] Mephisto version: {MEPHISTO_REPO.head.commit.hexsha[:7]}"
            )

        async with self.stage("cleanup"):
            logger.info("[MephistoService] Current stage: cleanup")
