import kayaku
from launart import Launart, Service
from launart.status import Phase
from loguru import logger

from mephisto.library.util.const import TEMPORARY_FILES_ROOT
from mephisto.library.util.orm.base import DatabaseEngine
from mephisto.library.util.orm.registry import DatabaseRegistry
from mephisto.library.util.orm.table import (
    RecordTable,
    AttachmentTable,
    ConfigTable,
    StatisticsTable,
)


class DataService(Service):
    id = "mephisto.service/data"
    registry: DatabaseRegistry

    @property
    def required(self):
        return set()

    @property
    def stages(self) -> set[Phase]:
        return {"preparing", "cleanup"}

    @staticmethod
    def ensure_temp():
        if not TEMPORARY_FILES_ROOT.is_dir():
            TEMPORARY_FILES_ROOT.mkdir(parents=True)
            logger.success("[DataService] Created temporary files root")
            return
        if files := list(TEMPORARY_FILES_ROOT.glob("*")):
            for file in files:
                file.unlink()
            logger.success(f"[DataService] Eliminated {len(files)} temporary files")

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.ensure_temp()

            kayaku.bootstrap()
            kayaku.save_all()
            logger.success("[DataService] Initialized all configurations")

            self.registry = DatabaseRegistry()
            main_engine = await self.registry.create("main")
            await main_engine.create(ConfigTable)
            await main_engine.create(AttachmentTable)
            await main_engine.create(StatisticsTable)
            logger.success("[DataService] Initialized main database")

            @self.registry.hook
            async def create_all(engine: DatabaseEngine):
                await engine.create(RecordTable)
                await engine.create(ConfigTable)
                await engine.create(StatisticsTable)

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.success("[DataService] Saved all configurations")

            for db_name, database in self.registry.databases.items():
                logger.debug(f"[DataService] Closing database {db_name}")
                await database.close()

            logger.success("[DataService] Closed all databases")
