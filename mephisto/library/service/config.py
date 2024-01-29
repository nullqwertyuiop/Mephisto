import kayaku
from launart import Launart, Service
from loguru import logger


class ConfigService(Service):
    id = "mephisto.service/config"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            logger.success("[ConfigService] 数据库初始化完成")
            kayaku.bootstrap()
            kayaku.save_all()
            logger.success("[ConfigService] 已保存配置文件")

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.success("[ConfigService] 已保存配置文件")
