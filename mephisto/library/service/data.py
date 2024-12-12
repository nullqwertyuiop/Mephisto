import kayaku
from launart import Launart, Service
from launart.status import Phase
from loguru import logger

from mephisto.library.util.const import TEMPORARY_FILES_ROOT
from mephisto.library.util.orm.base import DatabaseEngine
from mephisto.library.util.orm.registry import DatabaseRegistry
from mephisto.library.util.orm.table import (
    AttachmentTable,
    CacheTable,
    ConfigTable,
    PermissionTable,
    RecordTable,
    StatisticsTable,
)


class DataService(Service):
    id = "mephisto.service/data"
    registry: DatabaseRegistry

    @property
    def required(self):
        return {"web.render/graiax.playwright"}

    @property
    def stages(self) -> set[Phase]:
        return {"preparing", "blocking", "cleanup"}

    async def get_main_engine(self):
        return await self.registry.create("main")

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
        self.registry = DatabaseRegistry()

        async with self.stage("preparing"):
            self.ensure_temp()

            kayaku.bootstrap()
            kayaku.save_all()
            logger.success("[DataService] Initialized all configurations")

            main_engine = await self.registry.create("main")
            await main_engine.create(ConfigTable)
            await main_engine.create(AttachmentTable)
            await main_engine.create(StatisticsTable)
            await main_engine.create(CacheTable)
            await main_engine.create(PermissionTable)

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
